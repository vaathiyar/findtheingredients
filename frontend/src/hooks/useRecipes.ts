import { useState, useEffect } from 'react';
import { getRecipes } from '@/api/recipes';
import type { Recipe } from '@/types';

export function useRecipes() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    getRecipes()
      .then(setRecipes)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  return { recipes, loading, error };
}
