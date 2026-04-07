from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from shared.db.recipes import RecipeData, get_recipe_by_id, get_recipe_by_slug, list_recipes

router = APIRouter(prefix="/api", tags=["recipes"])


@router.get("/recipes")
def get_recipes_list() -> list[dict]:
    return list_recipes()


@router.get("/recipe")
def get_recipe(
    id: Annotated[UUID | None, Query()] = None,
    slug: Annotated[str | None, Query()] = None,
) -> RecipeData:
    if id is not None:
        data = get_recipe_by_id(id)
    elif slug is not None:
        data = get_recipe_by_slug(slug)
    else:
        raise HTTPException(status_code=400, detail="Provide either id or slug")
    if data is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return data
