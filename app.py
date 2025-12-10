from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.logging_config import configure_logging
from api.auth import router as auth_router
from api.sac.sac_account import router as sac_account_router
from api.sac.sac_policies import router as sac_policies_router
from api.sac.search_sac_account import router as search_sac_account_router
from api.sac.loss_run_distribution import router as loss_run_distribution_router
from api.sac.claim_review_distribution import router as claim_review_distribution_router
from api.sac.deduct_bill_distribution import router as deduct_bill_distribution_router
from api.sac.loss_run_frequency import router as loss_run_frequency_router
from api.sac.claim_review_frequency import router as claim_review_frequency_router
from api.sac.deduct_bill_frequency import router as deduct_bill_frequency_router
from api.sac.sac_affiliates import router as sac_affiliates_router
from api.sac.hcm_users import router as hcm_users_router

configure_logging()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])

#sac
app.include_router(sac_account_router, prefix="/sac_account", tags=["sac_account"])
app.include_router(sac_policies_router, prefix="/sac_policies", tags=["sac_policies"])
app.include_router(search_sac_account_router, prefix="/search_sac_account", tags=["search_sac_account"])

app.include_router(loss_run_distribution_router, prefix="/loss_run_distribution", tags=["loss_run_distribution"])
app.include_router(claim_review_distribution_router, prefix="/claim_review_distribution", tags=["claim_review_distribution"])
app.include_router(deduct_bill_distribution_router, prefix="/deduct_bill_distribution", tags=["deduct_bill_distribution"])

app.include_router(loss_run_frequency_router, prefix="/loss_run_frequency", tags=["loss_run_frequency"])
app.include_router(claim_review_frequency_router, prefix="/claim_review_frequency", tags=["claim_review_frequency"])
app.include_router(deduct_bill_frequency_router, prefix="/deduct_bill_frequency", tags=["deduct_bill_frequency"])

app.include_router(sac_affiliates_router, prefix="/sac_affiliates", tags=["sac_affiliates"])
app.include_router(hcm_users_router, prefix="/hcm_users", tags=["hcm_users"])
