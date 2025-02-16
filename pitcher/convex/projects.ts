import { mutation } from "./_generated/server";
import { v } from "convex/values";
import { getAuthUserId } from "@convex-dev/auth/server";

export const create = mutation({
  args: {
    githubUrl: v.string(),
    driveUrl: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) {
      throw new Error("Not authenticated");
    }

    const projectId = await ctx.db.insert("projects", {
      userId,
      githubUrl: args.githubUrl,
      driveUrl: args.driveUrl,
      status: "pending",
      createdAt: Date.now(),
    });

    return projectId;
  },
}); 