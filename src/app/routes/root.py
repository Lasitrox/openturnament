from starlette.requests import Request


def add_root_routes(router, templates):
    @router.get("/")
    def index(request: Request):
        """Home page - generates an image and name of a random artist."""
        return templates.TemplateResponse(
            "main.html",
            {
                "request": request,
            },
        )


    @router.get("/about")
    def about(request: Request):
        """About page - some background information about this app."""
        return templates.TemplateResponse("about.html", {"request": request})
