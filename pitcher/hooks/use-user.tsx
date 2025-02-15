"use client"

import { api } from "@/convex/_generated/api"
import { useQuery } from "convex/react"

/**
 * Hook for getting the current user
 * @returns the user object from the database. Loading state is undefined. Throws error if user is not signed in or account was deleted.
 */
export function useUser() {
  const user = useQuery(api.users.viewer)
  return user
}
