from typing import Optional

from fastapi import APIRouter, Query, Depends, HTTPException, Path
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from database import get_db
from src.dto.request import RequestUpdate, UserRequests, RequestModel, CategoryModel, RequestModelNoLike
from src.models.request import RequestLikes, Request, Category, RequestCategory
from src.models.user import User
from src.services.profile import get_current_user
from src.services.user_requests import get_user_requests, get_requests

router = APIRouter()

@router.get("/requests/user/", response_model=UserRequests)
async def get_user_requests_by_token(
    current_user_data: Request = Depends(get_user_requests),
    limit: int = Query(1, ge=1),
    page: int = Query(1, ge=1),
):
    offset = (page - 1) * limit
    requests, total_requests = current_user_data
    return {"requests": requests[offset:offset + limit], "requestsCount": total_requests}







@router.get("/requests/")
async def get_requests(
        current_user_data: Request = Depends(get_requests),
        limit: int = Query(1, ge=1),
        page: int = Query(1, ge=1),
        location: Optional[str] = None,
        categories: Optional[str] = None
):
    offset = (page - 1) * limit
    total_requests, requests = current_user_data
    if location:
        requests = [req for req in requests if req['location'] == location]
        total_requests = len(requests)
    return {"count": total_requests, "requests": requests[offset:offset + limit]}




@router.get("/requests/{request_id}")
async def get_request_by_id(request_id: int,
                             current_user: User = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    request = db.query(Request).filter(Request.id == request_id).first()
    if request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    user = db.query(User).filter(User.id == request.user_id).first()

    categories = db.query(Category).join(RequestCategory).filter(RequestCategory.request_id == request_id).all()

    category_ids = [category.id for category in categories]
    user_data = {"email": user.email, "username": user.username, "phone_number": user.phone_number}


    request_model = RequestModelNoLike(
        requestId=request.id,
        description=request.description,
        location=request.location,
        categories=category_ids,
        user=user_data
    )

    return request_model


@router.delete("/requests/delete/{request_id}")
async def delete_user_request(
        request_id: int = Path(..., title="The ID of the request to delete"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    request = db.query(Request).filter(Request.id == request_id).first()

    if request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the author of this request")

    db.query(RequestCategory).filter(RequestCategory.request_id == request_id).delete()

    db.query(RequestLikes).filter(RequestLikes.request_id == request_id).delete()

    db.delete(request)
    db.commit()

    return {"message": "Request deleted successfully"}


@router.put("/requests/edit/{request_id}")
async def edit_request(request_id: int, request_data: RequestUpdate,
                       current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    request = db.query(Request).filter(Request.id == request_id).first()
    if request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the author of this request")

    if request_data.description is not None:
        request.description = request_data.description
    if request_data.location is not None:
        request.location = request_data.location

    if request_data.categories is not None:
        request_categories = []
        for category_id in request_data.categories:
            category = db.query(Category).filter(Category.id == category_id).first()
            if category:
                request_categories.append(RequestCategory(request_id=request.id, category_id=category_id))

        existing_categories = db.query(RequestCategory).filter(RequestCategory.request_id == request_id)
        for existing_category in existing_categories:
            if existing_category.category_id not in request_data.categories:
                db.delete(existing_category)

        request.request_categories = request_categories

    db.commit()
    return {"message": "Request updated successfully"}


@router.post("/requests/like/{request_id}")
async def toggle_like_request(
    request_id: int = Path(..., title="The ID of the request to like"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    request = db.query(Request).filter(Request.id == request_id).first()

    if request:
        if current_user.role == 'ROLE_USER':
            existing_like = db.query(RequestLikes).filter(
                RequestLikes.request_id == request_id,
                RequestLikes.user_id == current_user.id
            ).first()

            if existing_like:
                db.delete(existing_like)
                db.commit()
                return {"message": "Like removed successfully"}
            else:
                like = RequestLikes(request_id=request_id, user_id=current_user.id)
                db.add(like)
                db.commit()
                return {"message": "Like added successfully"}
        else:
            raise HTTPException(status_code=403, detail="You are not a helper")
    else:
        raise HTTPException(status_code=404, detail="Request not found")


