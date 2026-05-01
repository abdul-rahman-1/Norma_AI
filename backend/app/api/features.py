from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.security import get_current_user, require_role
from app.db.mongodb import get_db
import importlib
import sys
import os
import traceback

router = APIRouter(prefix="/features", tags=["features"])

# Ensure the render directory is in the system path for dynamic imports
# We calculate it relative to this file's directory: backend/app/api/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RENDER_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", "render"))
if RENDER_PATH not in sys.path:
    sys.path.append(RENDER_PATH)

@router.post("/execute/{feature_id}")
async def execute_feature(
    feature_id: str,
    params: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Dynamic bridge to execute features from the render microservice.
    Feature ID format: A1_nlp_onboarding, B24_bulk_shift, etc.
    """
    try:
        # Determine the sub-package based on the feature prefix
        if feature_id.startswith("B"):
            module_path = f"app.features.clinical_features.{feature_id}"
        else:
            raise HTTPException(status_code=400, detail="Invalid feature ID format or access restricted to clinical features only.")

        # Dynamically import the module
        try:
            # We use importlib to reload or import the module from the render path
            # Note: app package inside render needs to be accessible. 
            # Since both backend/app and render/app exist, we might have a namespace conflict.
            # To avoid this, we can use a more specific import or rename the render app if needed.
            # However, the user said 'do not merge the folders'.
            
            # Temporary workaround: Use a custom loader or direct path import if namespace collisions occur.
            module = importlib.import_module(module_path)
        except ImportError as e:
            print(f"Import Error: {e}")
            raise HTTPException(status_code=404, detail=f"Feature module {feature_id} not found in render service.")

        if not hasattr(module, "execute"):
            raise HTTPException(status_code=500, detail=f"Feature module {feature_id} does not have an 'execute' function.")

        # Execute the feature logic
        # render features signature: execute(params, user_role, user_data=None, sender_phone=None)
        user_role = current_user.get("role", "PATIENT").upper()
        sender_phone = current_user.get("phone_number")
        
        result = await module.execute(
            params=params,
            user_role=user_role,
            user_data=current_user,
            sender_phone=sender_phone
        )
        
        return result

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
