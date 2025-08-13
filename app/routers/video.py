# app/routers/video.py
from __future__ import annotations

from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_database, get_default_user_id
from app.schemas.video import (
    VideoResponse,
    VideoWithSectionsResponse,
    SectionGroupResponse,
    SwingSectionResponse,
)
from app.crud import video_crud, section_group_crud, swing_section_crud

router = APIRouter(tags=["videos"])

@router.get("/video/{video_id}", response_model=VideoResponse)
async def get_video_details(
    video_id: UUID,
    db: AsyncSession = Depends(get_database),
):
    """
    Get detailed information about a specific video
    """
    try:
        video = await video_crud.get_video(db, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="動画が見つかりません")
        return video
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"動画詳細の取得に失敗しました: {str(e)}")

@router.get("/video/{video_id}/with-sections", response_model=VideoWithSectionsResponse)
async def get_video_with_sections(
    video_id: UUID,
    db: AsyncSession = Depends(get_database),
):
    """
    Get video with all coaching sections and comments
    """
    try:
        video = await video_crud.get_video_with_sections(db, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="動画が見つかりません")

        # 最初の SectionGroup を選択（なければ None）
        section_group = video.section_groups[0] if video.section_groups else None

        # VideoResponse をベースに合成
        base = VideoResponse.model_validate(video, from_attributes=True).model_dump()
        response = {
            **base,
            "section_group": SectionGroupResponse.model_validate(section_group, from_attributes=True).model_dump()
            if section_group else None,
            "sections": [
                SwingSectionResponse.model_validate(s, from_attributes=True).model_dump()
                for s in (section_group.sections if section_group else [])
            ],
        }
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"動画とセクション情報の取得に失敗しました: {str(e)}")

@router.get("/video/{video_id}/feedback-summary")
async def get_video_feedback_summary(
    video_id: UUID,
    db: AsyncSession = Depends(get_database),
):
    """
    Summarize feedback for a video
    """
    try:
        video = await video_crud.get_video_with_sections(db, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="動画が見つかりません")

        feedback_summary: Dict[str, Any] = {
            "video_id": str(video_id),
            "video_info": {
                "club_type": video.club_type,
                "swing_form": video.swing_form,
                "swing_note": video.swing_note,
                "upload_date": video.upload_date,
            },
            "total_sections": 0,
            "sections_with_comments": 0,
            "feedback_sections": [],
        }

        if video.section_groups and video.section_groups[0].sections:
            sections = video.section_groups[0].sections
            feedback_summary["total_sections"] = len(sections)

            for section in sections:
                section_data: Dict[str, Any] = {
                    "section_id": str(section.section_id),
                    "time_range": f"{section.start_sec}-{section.end_sec}秒",
                    "tags": section.tags or [],
                    "has_comment": bool(section.coach_comment),
                    "comment_summary": section.coach_comment_summary,
                }
                if section.coach_comment:
                    feedback_summary["sections_with_comments"] += 1
                    section_data["full_comment"] = section.coach_comment

                feedback_summary["feedback_sections"].append(section_data)

        return feedback_summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"フィードバック要約の取得に失敗しました: {str(e)}")

@router.get("/videos", response_model=List[VideoResponse])
async def get_all_videos(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_database),
):
    """
    Get all videos for coach dashboard (all users)
    """
    try:
        # sections を一緒にロードしたいときは get_all_videos_with_sections を使うが、
        # レスポンスモデルが VideoResponse のためここでは基本情報のみ返す想定
        videos = await video_crud.get_all_videos_with_sections(db, skip, limit)
        # VideoResponse でシリアライズできるのでそのまま返却
        return videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"全動画一覧の取得に失敗しました: {str(e)}")

@router.get("/videos/search")
async def search_videos(
    user_id: Optional[str] = Query(None, description="User ID (uses default if not provided)"),
    club_type: Optional[str] = Query(None, description="Filter by club type"),
    swing_form: Optional[str] = Query(None, description="Filter by swing form"),
    has_feedback: Optional[bool] = Query(None, description="Filter videos with/without feedback"),
    db: AsyncSession = Depends(get_database),
):
    """
    Search and filter videos based on criteria
    """
    try:
        actual_user_id = user_id if user_id else get_default_user_id()

        # ユーザーの全動画（必要に応じて最適化可）
        videos = await video_crud.get_videos_by_user(db, UUID(actual_user_id))

        filtered = []
        for v in videos:
            if club_type and v.club_type != club_type:
                continue
            if swing_form and v.swing_form != swing_form:
                continue
            if has_feedback is not None:
                has_sections = bool(v.section_groups)
                if has_feedback != has_sections:
                    continue
            filtered.append(v)

        return {
            "total_found": len(filtered),
            "filters_applied": {
                "club_type": club_type,
                "swing_form": swing_form,
                "has_feedback": has_feedback,
            },
            "videos": filtered,
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="無効なユーザーIDです")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"動画検索に失敗しました: {str(e)}")
