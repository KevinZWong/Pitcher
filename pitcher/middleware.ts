import {
  convexAuthNextjsMiddleware,
  createRouteMatcher,
  nextjsMiddlewareRedirect,
} from "@convex-dev/auth/nextjs/server";

const isSignInPage = createRouteMatcher(["/auth"]);
const isOnboardingPage = createRouteMatcher(["/onboarding"]);
const isProtectedRoute = createRouteMatcher(["/dashboard(.*)"]);

/**
 * Configure routes in here for protected and unprotected routes as well as redirects
 */
export default convexAuthNextjsMiddleware(async (request, { convexAuth }) => {
  const isAuthenticated = await convexAuth.isAuthenticated();
  
  if (isSignInPage(request) && isAuthenticated) {

    return nextjsMiddlewareRedirect(request, "/dashboard");
  }
  
  if (isProtectedRoute(request) && !isAuthenticated) {
    return nextjsMiddlewareRedirect(request, "/auth");
  }

  if (isOnboardingPage(request) && !isAuthenticated) {
    return nextjsMiddlewareRedirect(request, "/auth");
  }
});

export const config = {
  // The following matcher runs middleware on all routes
  // except static assets.
  matcher: ["/((?!.*\\..*|_next).*)", "/", "/(api|trpc)(.*)"],
};
