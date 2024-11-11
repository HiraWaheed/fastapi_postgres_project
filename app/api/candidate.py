import logging
from typing import Optional
from sqlalchemy import or_
from app.api.user import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import app.models.candidate as CandidateModel
import app.models.user as UserModel
from app.database import get_db
import app.schemas.candidate as candidate_schema


router = APIRouter()


@router.post(
    "/candidates", response_model=candidate_schema.CandidateCreateResponse | str
)
def add_candidate(
    candidate_data: candidate_schema.CandidateBase,
    db: Session = Depends(get_db),
    current_user: UserModel.User = Depends(get_current_user),
):
    """Endpoint to add a candidate
    Args:
        candidate data (CandidateBase)
        Session (database session)
        current_user (UserModel)
    Returns:
        candidate(CandidateCreateResponse | str): newly created candidate id
    """
    try:
        # Create new candidate profile
        new_candidate = CandidateModel.Candidate(
            user_id=current_user.id,
            first_name=candidate_data.first_name,
            last_name=candidate_data.last_name,
            experience=candidate_data.experience,
        )

        db.add(new_candidate)
        db.commit()
        db.refresh(new_candidate)

        return candidate_schema.CandidateCreateResponse(id=new_candidate.id)
    except HTTPException as e:
        logging.error(f"HTTPException occurred at add_candidate: {e.detail}")
        return e.detail
    except Exception as e:
        logging.error(f"Error occurred at add_candidate{e}")
        return "Something went wrong while adding candidate profile"


@router.get("/candidates/{id}", response_model=candidate_schema.CandidateBase | str)
def fetch_candidate(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserModel.User = Depends(get_current_user),
):
    """Endpoint to add a candidate
    Args:
        id (int)
        Session (database session)
        current_user (UserModel)
    Returns:
        candidate (CandidateBase | str): candidate fetched
    """
    try:
        candidate = (
            db.query(CandidateModel.Candidate)
            .filter(CandidateModel.Candidate.id == id)
            .first()
        )
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return candidate
    except HTTPException as e:
        logging.error(f"HTTPException occurred at fetch_candidate: {e.detail}")
        return e.detail
    except Exception as e:
        logging.error(f"Error occurred at fetch_candidate{e}")
        return "Something went wrong while fetching candidate profile"


@router.put("/candidates/{id}", response_model=candidate_schema.CandidateBase | str)
def update_candidate(
    id: int,
    candidate_data: candidate_schema.CandidateBase,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Endpoint to add a candidate
    Args:
        id (int)
        Session (database session)
        current_user (UserModel)
    Returns:
        candidate (CandidateBase | str): candidate fetched with updated details
    """
    try:
        candidate = (
            db.query(CandidateModel.Candidate)
            .filter(CandidateModel.Candidate.id == id)
            .first()
        )
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Update the candidate
        candidate.first_name = candidate_data.first_name
        candidate.last_name = candidate_data.last_name
        candidate.experience = candidate_data.experience
        db.commit()
        db.refresh(candidate)

        return candidate
    except HTTPException as e:
        logging.error(f"HTTPException occurred at update_candidate: {e.detail}")
        return e.detail
    except Exception as e:
        logging.error(f"Error occurred at updating_candidate{e}")
        return "Something went wrong while updating candidate profile"


@router.delete("/candidates/{id}", response_model=candidate_schema.CandidateBase | str)
def delete_candidate(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Endpoint to delete a candidate
    Args:
        id (int)
        Session (database session)
        current_user (UserModel)
    Returns:
        candidate (CandidateBase | str): candidate fetched & deleted
    """
    try:
        candidate = (
            db.query(CandidateModel.Candidate)
            .filter(CandidateModel.Candidate.id == id)
            .first()
        )
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        db.delete(candidate)
        db.commit()

        return candidate

    except HTTPException as e:
        logging.error(f"HTTPException occurred at delete_candidate: {e.detail}")
        return e.detail
    except Exception as e:
        logging.error(f"Something went wrong: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong.",
        )


@router.get("/all-candidates", response_model=dict | str)
def fetch_all_candidates(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    search_by_name: Optional[str] = None,
    search_by_experience: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
):
    """Endpoint to fetch all candidates
    Args:
        Session (database session)
        current_user (UserModel)
        search_by_name (str): search filter
        search_by_experience (int): search filter
        page (str): pagination number
        page_size (str): pagination size
    Returns:
        dict: Dictionary with searched candidates and pagination info
    """
    try:
        search_filter = []
        if search_by_name:
            search_filter.append(
                or_(
                    CandidateModel.Candidate.first_name.ilike(f"%{search_by_name}%"),
                    CandidateModel.Candidate.last_name.ilike(f"%{search_by_name}%"),
                )
            )
        if search_by_experience:
            search_filter.append(
                or_(CandidateModel.Candidate.experience == search_by_experience)
            )
        query = db.query(CandidateModel.Candidate).filter(*search_filter)
        total_candidates = query.count()

        # Apply pagination according to page info given
        candidates = query.offset((page - 1) * page_size).limit(page_size).all()

        total_pages = (total_candidates + page_size - 1) // page_size

        if not candidates:
            raise HTTPException(status_code=404, detail="No candidates found.")

        return {
            "total_candidates": total_candidates,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "candidates": [
                candidate_schema.CandidateBase.from_orm(candidate)
                for candidate in candidates
            ],
        }

    except HTTPException as e:
        logging.error(f"HTTPException occurred at fetch_all_candidates: {e.detail}")
        return e.detail

    except Exception as e:
        logging.error(f"Error occurred at fetch_all_candidates: {e}")
        return "Something went wrong while fetching all candidates profile"
