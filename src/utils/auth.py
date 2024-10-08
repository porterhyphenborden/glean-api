import jwt


def user_is_authorized_for_endpoint(path_params: dict[str, str], token: str) -> bool:
    """
    Checks user_id from request path against user sub in token, and returns a 
    boolean representing whether or not the user is authorized for this request.
    """
    user_from_path = path_params.get("user_id")
    decoded_token = jwt.decode(token, options={"verify_signature": False})
    user_id_from_token = decoded_token.get("sub")

    if user_from_path != user_id_from_token:
        return False
    
    return True
