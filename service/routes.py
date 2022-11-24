"""
Employe Service

This microservice handles the lifecycle of Employes
"""
# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for   # noqa; F401
from service.models import Employed, Beneficiary
from service.common import status, util  # HTTP Status Codes
from . import app  # Import Flask application

############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


@app.route("/error")
def error():
    """Error Status"""
    abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "Server Error")


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Employes REST API Service",
            version="1.0",
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW EMPLOYED
######################################################################
@app.route("/employe", methods=["POST"])
def create_employes():
    """
    Creates an Employe
    This endpoint will create an Employe based the data in the body that is posted
    """
    app.logger.info("Request to create an Employe")
    check_content_type("application/json")
    try:
        employe_data = request.get_json()["employe"]
        beneficiary_data = request.get_json()["beneficiary"]
    except KeyError:
        abort(status.HTTP_400_BAD_REQUEST)
    img = employe_data["photo"]
    url= util.upload_img(img,employe_data["name"])
    employe_data["photo"] = url
    employe = Employed()
    employe.deserialize(employe_data)
    employe.create()
    message = employe.serialize()
    message["beneficiaries"] = []
    if beneficiary_data is not None:
        for b in beneficiary_data:
            beneficiary = Beneficiary()
            beneficiary.deserialize(b)
            beneficiary.employed_id = employe.id
            beneficiary.create()
            message["beneficiaries"] = message["beneficiaries"].append(beneficiary.serialize())
     #Uncomment once get_accounts has been implemented
     #location_url = url_for("get_accounts", account_id=account.id, _external=True)
    location_url = "/"  # Remove once get_accounts has been implemented
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# LIST ALL ACCOUNTS
######################################################################


@app.route("/employe", methods=["GET"])
def list_accounts():
    """
    Read all Emplopyes.
    This endpoint will read all Accounts on the database.
    """
    app.logger.info("Request to list an Employe")
    employes = Employed.all()
    if not employes:
        abort(status.HTTP_404_NOT_FOUND, "Not Found Employes")
    employes = [a.serialize() for a in employes]
    return jsonify(employes), status.HTTP_200_OK

######################################################################
# READ AN ACCOUNT
######################################################################


@app.route("/employe/<int:employe_id>", methods=["GET"])
def read_an_account(employe_id):
    """
    Read an Employe.
    This endpoint will read an Account based on the id given in the url.
    """
    app.logger.info("Request to read an Account")
    employe = Employed.find(employe_id)
    if not employe:
        abort(status.HTTP_404_NOT_FOUND, f"Employe [{employe_id}] not found")
    return employe.serialize(), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING EMPLOYE
######################################################################

@app.route("/employe/<int:employe_id>", methods=["PUT"])
def update_account(employe_id):
    """
    Update an Employe.
    This endpoint will update an exit Account based on the data given in the body.
    """
    app.logger.info("Request to update an Account")
    employe = Employed.find(employe_id)
    if not employe:
        abort(status.HTTP_404_NOT_FOUND, f"Employe [{employe_id}] not found")
    employe.deserialize(request.get_json())
    employe.update()
    return employe.serialize(), status.HTTP_200_OK


######################################################################
# DELETE AN EMPLOYE
######################################################################

@app.route("/employe/<int:employe_id>", methods=["DELETE"])
def delete_account(employe_id):
    """
    Delete an employe.
    This endpoint will delete an exit employe based on its id.
    """
    app.logger.info("Request to delete an employe")
    employe = Employed.find(employe_id)
    if not employe:
        abort(status.HTTP_404_NOT_FOUND, f"Employe [{employe}] not found")
    employe.status = "false"
    employe.update()
    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
