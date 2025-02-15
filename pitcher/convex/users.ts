import { getAuthUserId } from "@convex-dev/auth/server";
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const viewer = query({
  args: {},
  handler: async (ctx) => {
    const userId = await getAuthUserId(ctx);
    if (userId === null) {
      throw new Error("Not signed in");
    }
    const user = await ctx.db.get(userId);
    if (user === null) {
      throw new Error("User was deleted");
    }
    return user;
  },
});

export const update = mutation({
  args: {
    name: v.string(),
    email: v.optional(v.string()),
    hasCompletedOnboarding: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (userId === null) {
      throw new Error("Not signed in");
    }
    
    const updates: Record<string, string | boolean> = { name: args.name };
    if (args.email) {
      updates.email = args.email;
    }
    if (args.hasCompletedOnboarding !== undefined) {
      updates.hasCompletedOnboarding = args.hasCompletedOnboarding;
    }
    
    await ctx.db.patch(userId, updates);
  },
});
