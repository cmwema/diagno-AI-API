# Diagno AI
Get the full API documentation **[here](https://documenter.getpostman.com/view/22007181/2sA3Bj8tvB)**

## *Key Functionalities*
**User Authentication**
* Users can register for new accounts with email, first name, last name, and password.
* Email verification is required through a one-time password (OTP) sent to the registered email.
* Login functionality allows users to access the system using their email and password.
* JWT (JSON Web Token) based authentication is implemented for subsequent authorized requests.
* Users can initiate password reset by providing their email address.
* A password reset link is then sent to the user's email for completing the reset process.

**Disease Prediction Model**
* The API offers a prediction model where users can submit their symptoms to get a potential disease prediction.
* The request body includes a comma-separated list of user-reported symptoms.
* The response provides the predicted disease along with a description, precautions, medications, workout recommendations, and dietary suggestions.
* Separately, the API offers access to a comprehensive list of possible symptoms.

**User Profile Management**
* Users can update their profile information including an optional profile image, first name, and last name.
* Authorization is required through a JWT token in the request header.

**Important Note**

While this API seems to offer health diagnosis, it's crucial to understand that it should never replace consulting a licensed medical professional.
