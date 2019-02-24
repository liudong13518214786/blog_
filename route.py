from handler.handlers import *
handler = [
    (r"/", IndexHandler),
    (r"/detail/(\w+)", BlogDetailHandler),
    (r"/write", BlogWriteHandler),
    (r"/login", LoginHandler),
    (r"/jwt/create", JwtAuthHandler),
    (r"/logout", LogoutHandler),
    (r"/upload", UploadFileHandler),
    (r"/api/1.0/blog", ApiGetBlogHandler),

]