# RESTfull api task
This is a blog application built with FastAPI framework. 
It provides endpoints for user registration, user authentication, creating, updating, and deleting blog posts, and liking/disliking blog posts.



### Features
* User registration: New users can register by providing a unique username, email, and password. If the username or email already exists, the registration request will be rejected.

* User authentication: Registered users can log in to the application using their username and password. Upon successful authentication, a JWT access token will be provided, which can be used to authenticate subsequent requests.

* Create blog posts: Authenticated users can create new blog posts by providing a title and content for the post. The author of the post will be set to the currently logged-in user.

* Get all blog posts: Authenticated users can retrieve all existing blog posts.

* Get a specific blog post: Authenticated users can retrieve a specific blog post by its ID.

* Update blog posts: Authenticated users can update their own blog posts by providing a new title and content for the post. Only the author of the post can update it.

* Delete blog posts: Authenticated users can delete their own blog posts. Only the author of the post can delete it.

* Like/Dislike blog posts: Authenticated users can like or dislike blog posts. They cannot like their own posts. The like/dislike status will be stored and can be updated.



### Installation Requirements
 - Docker      

### Getting Started  
To build and run the project, follow these steps:   

- Build the project: `make build`
- Start the project: `make start`   
- Remove database artifacts: `make clean`   
- Restart the project (build and start): `make restart` 

API request examples can be found in the `RESTfull API task.postman_collection.json` in root folder.    
Swagger can be found in the "swagger.json" in root folder.

For more information about the API, run the app and open the following links:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc