import {
  TextField,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  Grid,
  Button,
  Tab,
  Tabs,
  Box,
  CircularProgress,
  useTheme,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import { useForm, Controller, FormProvider } from "react-hook-form";
import TabPanel from "../../../../ui/TabPanel";
import AccountService from "./AccountService";
import NcmTab from "./NcmTab";
import LossRunScheduling from "../LossRunScheduling";
import Notes from "../Notes";
import DeductibleBill from "./DeductibleBill";
import ClaimReviewScheduling from "../ClaimReviewScheduling";
import Shi from "../Shi";
import Modal from "../../../../ui/Modal";
import ViewPolicies from "../view-policies/ViewPolicies";
import ViewAffiliates from "../ViewAffiliates";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import api from "../../../../../api/api";
import Loader from "../../../../ui/Loader";
import { sacAccountFieldPermissions } from "../../../../../field-permissions";
import { useSelector } from "react-redux";
import Swal from "sweetalert2";

function convertDateFormat(inputDateString) {
  const date = new Date(inputDateString);

  if (isNaN(date.getTime())) return "Invalid Date";

  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const day = date.getDate().toString().padStart(2, "0");

  return `${year}-${month}-${day}`;
}

const defaultValues = {
  AcctStatus: "Active",
  CustomerName: "",
  CustomerNum: "",
  SAC_Contact1: "",
  LossCtlRep1: "",
  DateCreated: new Date().toISOString().split("T")[0],
  RelatedEnt: "",
  DateNotif: "",
  SAC_Contact2: "Jenna Houle",
  LossCtlRep2: "",
  OnBoardDate: "",
  TermDate: "",
  AcctOwner: "",
  RiskSolMgr: "",
  OBMethod: "",
  TermCode: "",
  // CreatedBy: "",
  BranchName: "",
  MarketSegmentation: "",
  AccountNotes: "",
  // Account Service
  ServicesReq: "",
  Exceptions: "",
  HCMAccess: "",
  TotalPrem: "",
  ExceptType: "",
  DiscDate: "",
  BusinessType: "",
  AccomForm: "",
  RenewLetterDt: "",
  ServLevel: "",
  AccomType: "",
  InsuredWebsite: "",
  HCM_LOC_ONLY: "No",
  // ncm
  NCMType: "",
  NCMStatus: "",
  NCMStartDt: "",
  NCMEndDt: "",
  NCMTermReason: "",
  NCMComments: "",
  // Loss Run Scheduling
  LossRunDistFreq: "",
  LossRunCheckboxes: [
    { checked: false, lastSendDate: "" },
    { checked: false, lastSendDate: "" },
    { checked: false, lastSendDate: "" },
    { checked: false, lastSendDate: "" },
    { checked: false, lastSendDate: "" },
    { checked: false, lastSendDate: "" },
    { checked: false, lastSendDate: "" },
    { checked: false, lastSendDate: "" },
    { checked: false, lastSendDate: "" },
    { checked: false, lastSendDate: "" },
    { checked: false, lastSendDate: "" },
    { checked: false, lastSendDate: "" },
  ],
  // // Loss Run Notes
  LossRunNotes: "",
  // // Deductible Bill
  DeductNotes: "",
  DeductDistFreq: "",
  DeductCheckboxes: [
    false,
    false,
    false,
    false,
    false,
    false,
    false,
    false,
    false,
    false,
    false,
    false,
  ],
  // // Claim Review Scheduling
  ClaimRevDistFreq: "",
  CRThresh: "50000",
  ClaimRevCheckboxes: [
    {
      checked: false,
      lastSendDate: "",
      reportType: "",
      deliveryMethod: "",
      narrativesProcessed: "",
    },
    {
      checked: false,
      lastSendDate: "",
      reportType: "",
      deliveryMethod: "",
      narrativesProcessed: "",
    },
    {
      checked: false,
      lastSendDate: "",
      reportType: "",
      deliveryMethod: "",
      narrativesProcessed: "",
    },
    {
      checked: false,
      lastSendDate: "",
      reportType: "",
      deliveryMethod: "",
      narrativesProcessed: "",
    },
    {
      checked: false,
      lastSendDate: "",
      reportType: "",
      deliveryMethod: "",
      narrativesProcessed: "",
    },
    {
      checked: false,
      lastSendDate: "",
      reportType: "",
      deliveryMethod: "",
      narrativesProcessed: "",
    },
    {
      checked: false,
      lastSendDate: "",
      reportType: "",
      deliveryMethod: "",
      narrativesProcessed: "",
    },
    {
      checked: false,
      lastSendDate: "",
      reportType: "",
      deliveryMethod: "",
      narrativesProcessed: "",
    },
    {
      checked: false,
      lastSendDate: "",
      reportType: "",
      deliveryMethod: "",
      narrativesProcessed: "",
    },
    {
      checked: false,
      lastSendDate: "",
      reportType: "",
      deliveryMethod: "",
      narrativesProcessed: "",
    },
    {
      checked: false,
      lastSendDate: "",
      reportType: "",
      deliveryMethod: "",
      narrativesProcessed: "",
    },
    {
      checked: false,
      lastSendDate: "",
      reportType: "",
      deliveryMethod: "",
      narrativesProcessed: "",
    },
  ],
  // Claim Review Notes
  ClaimRevNotes: "",
  // shi
  SHI_Complete: "Yes",
  SHI_Comments: "",
  // Change Notes
  ChangeNotes: "",
};

const SacCreateNewAccount = () => {
  const methods = useForm({ defaultValues });
  const { control, handleSubmit, reset, setValue, getValues } = methods;
  const [tabIndex, setTabIndex] = useState(0);
  const [viewPolicies, setViewPolicies] = useState(false);
  const [viewAffiliates, setViewAffiliates] = useState(false);
  const { column_name } = useParams();
  const [loading, setLoading] = useState(false);
  const user = useSelector((state) => state.auth.user);
  const allowedFields = sacAccountFieldPermissions[user.role];
  const { pathname, state } = useLocation();
  const from = state?.from || "/pending-items";
  const [submitOrSave, setSubmitOrSave] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const theme = useTheme();
  const [accountStatus, setAccountStatus] = useState("Active");
  const [haveOtherRelatedAccounts, setHaveOtherRelatedAccounts] = useState("");

  const isEnabled = (fieldName) => {
    if (allowedFields === "ALL") return true;
    return allowedFields?.includes(fieldName);
  };

  const onSubmit = async (data, e) => {
    const operation = e.nativeEvent.submitter.name;

    const filteredData = Object.fromEntries(
      Object.entries(data).filter(
        ([_, v]) => v !== null && v !== "" && v !== undefined
      )
    );

    const dataValidationFailedFor =
      isEnabled("CustomerNum") && !filteredData.CustomerNum
        ? "Customer Number"
        : isEnabled("CustomerName") && !filteredData.CustomerName
        ? "Account Name"
        : isEnabled("OnBoardDate") && !filteredData.OnBoardDate
        ? "On Board Date"
        : isEnabled("BranchName") && !filteredData.BranchName
        ? "Branch Name"
        : isEnabled("DateNotif") &&
          filteredData.AcctStatus === "Inactive" &&
          !filteredData.DateNotif
        ? "Notification Date"
        : isEnabled("TermDate") &&
          filteredData.AcctStatus === "Inactive" &&
          !filteredData.TermDate
        ? "Termination Date"
        : isEnabled("TermCode") &&
          filteredData.AcctStatus === "Inactive" &&
          !filteredData.TermCode
        ? "Termination Reason"
        : "";

    //data validation alert when mandatory fields are missing
    if (dataValidationFailedFor) {
      Swal.fire({
        title: "Data Validation Error",
        text: `${dataValidationFailedFor} is mandatory and cannot be empty!`,
        icon: "error",
        confirmButtonText: "OK",
        iconColor: theme.palette.error.main,
        customClass: {
          confirmButton: "swal-confirm-button",
          cancelButton: "swal-cancel-button",
        },
        buttonsStyling: false,
      });
      return;
    }

    //alerts for service level & total permium conflicts
    const totalPrem = filteredData.TotalPrem;
    const serviceLevel = filteredData.ServLevel;
    if (
      pathname !== "/sac-create-new-account" &&
      state?.from !== "/pending-items" &&
      ((totalPrem !== 0 &&
        (serviceLevel === "Decuctible Billing - Special Accounts" ||
          serviceLevel === "Loss Run" ||
          serviceLevel === "Deductible Billing - Paragon" ||
          serviceLevel === "Inactive")) ||
        (totalPrem < 750000 && serviceLevel === "Comprehensive") ||
        ((totalPrem < 500000 || totalPrem > 750000) &&
          serviceLevel === "Enhanced") ||
        ((totalPrem < 250000 || totalPrem > 500000) &&
          serviceLevel === "Essential") ||
        ((totalPrem < 150000 || totalPrem > 250000) &&
          serviceLevel === "Primary") ||
        ((totalPrem < 0 || totalPrem > 150000) && serviceLevel === "Exception"))
    ) {
      const res = await Swal.fire({
        title: "Service Level Conflict",
        text: "Total Active Policy Premium is in conflict with Service Level. Do you still want to save?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Yes",
        cancelButtonText: "No",
        iconColor: theme.palette.warning.main,
        customClass: {
          confirmButton: "swal-confirm-button",
          cancelButton: "swal-cancel-button",
        },
        buttonsStyling: false,
        cancelButtonColor: theme.palette.error.main,
      });

      if (res.dismiss === Swal.DismissReason.cancel) {
        Swal.fire({
          title: "Save Aborted",
          text: "Save procedure terminated by user.",
          icon: "info",
          confirmButtonText: "Ok",
          iconColor: theme.palette.info.main,
          customClass: {
            confirmButton: "swal-confirm-button",
            cancelButton: "swal-cancel-button",
          },
          buttonsStyling: false,
        });
        return;
      }
    }

    //confirmation alert on submission
    if (operation === "submit") {
      const res = await Swal.fire({
        title: "Confirm Submit",
        text: "This will save all the changes & close the account. Is that what you want to do?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Yes",
        cancelButtonText: "No",
        iconColor: theme.palette.warning.main,
        customClass: {
          confirmButton: "swal-confirm-button",
          cancelButton: "swal-cancel-button",
        },
        buttonsStyling: false,
        cancelButtonColor: theme.palette.error.main,
      });

      if (res.dismiss === Swal.DismissReason.cancel) return;
    }

    const updatedData =
      operation === "save"
        ? {
            ...filteredData,
            Stage: user.role,
            IsSubmitted:
              pathname !== "/sac-create-new-account" &&
              state?.from !== "/pending-items"
                ? 1
                : 0,
          }
        : { ...filteredData, Stage: user.role, IsSubmitted: 1 };

    const LossRunCheckboxes =
      updatedData.LossRunCheckboxes &&
      updatedData.LossRunCheckboxes.map((item, index) => {
        if (item.checked || item.lastSendDate)
          return {
            CustomerNum: updatedData.CustomerNum,
            MthNum: index + 1,
            RptMth: item.checked,
            CompDate: item.lastSendDate || null,
          };
        else return null;
      }).filter((item) => item);

    const DeductCheckboxes =
      updatedData.DeductCheckboxes &&
      updatedData.DeductCheckboxes.map((item, index) => {
        if (item)
          return {
            CustomerNum: updatedData.CustomerNum,
            MthNum: index + 1,
            RptMth: item,
          };
        else return null;
      }).filter((item) => item);

    const ClaimRevCheckboxes =
      updatedData.ClaimRevCheckboxes &&
      updatedData.ClaimRevCheckboxes.map((item, index) => {
        if (item.checked || item.lastSendDate)
          return {
            CustomerNum: updatedData.CustomerNum,
            MthNum: index + 1,
            RptMth: item.checked,
            CompDate: item.lastSendDate || null,
            RptType: item.reportType || null,
            DelivMeth: item.deliveryMethod || null,
            CRNumNarr: item.narrativesProcessed || null,
          };
        else return null;
      }).filter((item) => item);

    delete updatedData.LossRunCheckboxes;
    delete updatedData.DeductCheckboxes;
    delete updatedData.ClaimRevCheckboxes;

    setSubmitOrSave(operation);
    setError("");

    try {
      await Promise.all([
        api.post("/sac_account/upsert", updatedData),
        LossRunCheckboxes &&
          api.post("/loss_run_frequency/upsert", LossRunCheckboxes),
        DeductCheckboxes &&
          api.post("/deduct_bill_frequency/upsert", DeductCheckboxes),
        ClaimRevCheckboxes &&
          api.post("/claim_review_frequency/upsert", ClaimRevCheckboxes),
      ]);

      setSubmitOrSave("");
      if (operation === "submit") reset(defaultValues);
    } catch (err) {
      console.error(err);
      if (err.response) {
        setError(
          `Server error: ${err.response.data.detail || err.response.statusText}`
        );
      } else {
        setError("Network error: Unable to reach API");
      }
    } finally {
      const res = await Swal.fire({
        title: "Changes Saved",
        text: "Your changes have been saved",
        icon: "success",
        confirmButtonText: "OK",
        iconColor: theme.palette.success.main,
        customClass: {
          confirmButton: "swal-confirm-button",
          cancelButton: "swal-cancel-button",
        },
        buttonsStyling: false,
      });

      if (res.isConfirmed || res.dismiss) {
        setSubmitOrSave("");
        navigate(from, { replace: true });
      }
    }
  };

  const handleTabChange = (_, newValue) => setTabIndex(newValue);

  useEffect(() => {
    if (!column_name) {
      reset(defaultValues);
      return;
    }

    const fetchData = async (searchByColumn, value) => {
      try {
        setLoading(true);
        const [main, lossRun, deductBill, claimReview] = await Promise.all([
          api.get("/sac_account/", { params: { [searchByColumn]: value } }),
          api.get("/loss_run_frequency/", { params: { CustomerNum: value } }),
          api.get("/deduct_bill_frequency/", {
            params: { CustomerNum: value },
          }),
          api.get("/claim_review_frequency/", {
            params: { CustomerNum: value },
          }),
        ]);

        //replacing all null values with empty string
        const data = Object.fromEntries(
          Object.entries(main.data[0]).map(([k, v]) => [k, v === null ? "" : v])
        );

        let formattedData = {
          ...data,
          DateCreated: data.DateCreated ? data.DateCreated.split("T")[0] : "",
          DateNotif: data.DateNotif ? data.DateNotif.split("T")[0] : "",
          OnBoardDate: data.OnBoardDate ? data.OnBoardDate.split("T")[0] : "",
          TermDate: data.TermDate ? data.TermDate.split("T")[0] : "",
          DiscDate: data.DiscDate ? convertDateFormat(data.DiscDate) : "",
          RenewLetterDt: data.RenewLetterDt
            ? data.RenewLetterDt.split("T")[0]
            : "",
        };

        let LossRunCheckboxes = [];
        let DeductCheckboxes = [];
        let ClaimRevCheckboxes = [];

        for (let i = 1; i <= 12; i++) {
          LossRunCheckboxes.push({ checked: false, lastSendDate: "" });
          DeductCheckboxes.push(false);
          ClaimRevCheckboxes.push({
            checked: false,
            lastSendDate: "",
            reportType: "",
            deliveryMethod: "",
            narrativesProcessed: "",
          });
        }

        if (lossRun.data.length > 0) {
          lossRun.data.forEach((element) => {
            LossRunCheckboxes[element.MthNum - 1].checked =
              element.RptMth === 1;
            LossRunCheckboxes[element.MthNum - 1].lastSendDate =
              element.CompDate ? element.CompDate.split("T")[0] : "";
          });
          formattedData.LossRunCheckboxes = LossRunCheckboxes;
        }

        if (deductBill.data.length > 0) {
          deductBill.data.forEach((element) => {
            DeductCheckboxes[element.MthNum - 1] = element.RptMth === 1;
          });
          formattedData.DeductCheckboxes = DeductCheckboxes;
        }

        if (claimReview.data.length > 0) {
          claimReview.data.forEach((element) => {
            ClaimRevCheckboxes[element.MthNum - 1].checked =
              element.RptMth === 1;
            ClaimRevCheckboxes[element.MthNum - 1].lastSendDate =
              element.CompDate ? element.CompDate.split("T")[0] : "";
            ClaimRevCheckboxes[element.MthNum - 1].reportType = element.RptType;
            ClaimRevCheckboxes[element.MthNum - 1].deliveryMethod =
              element.DelivMeth;
            ClaimRevCheckboxes[element.MthNum - 1].narrativesProcessed =
              element.CRNumNarr;
          });
          formattedData.ClaimRevCheckboxes = ClaimRevCheckboxes;
        }

        setAccountStatus(formattedData.AcctStatus);
        setHaveOtherRelatedAccounts(formattedData.RelatedEnt);
        reset(formattedData);
      } catch (err) {
        console.error("Error fetching data", err);
      } finally {
        setLoading(false);
      }
    };

    const [key, value] = column_name.split("=");
    fetchData(key, value);
  }, [column_name, reset]);

  useEffect(() => {
    if (pathname === "/sac-create-new-account") setAccountStatus("Active");
  }, [pathname]);

  const handleCancel = async () => {
    const res = await Swal.fire({
      title: "Confirm Request to Cancel",
      text: "This will return you to the main menu, unsaved changes will be lost. Is this what you want to do?",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes",
      cancelButtonText: "No",
      iconColor: theme.palette.warning.main,
      customClass: {
        confirmButton: "swal-confirm-button",
        cancelButton: "swal-cancel-button",
      },
      buttonsStyling: false,
      cancelButtonColor: theme.palette.error.main,
    });

    if (res.isConfirmed) navigate(from, { replace: true });
  };

  if (error) console.log(error);

  if (loading) return <Loader size={40} height="800px" />;

  return (
    <>
      {pathname !== "/sac-create-new-account" &&
        state?.from !== "/pending-items" && (
          <>
            {/*Modal for view policies  */}
            <Modal
              open={viewPolicies}
              onClose={() => setViewPolicies(false)}
              maxWidth="xl"
            >
              <ViewPolicies
                CustomerNum={column_name.split("=")[1]}
                CustomerName={getValues("CustomerName")}
              />
            </Modal>

            {/*Modal for view affiliates  */}
            <Modal
              open={viewAffiliates}
              onClose={() => setViewAffiliates(false)}
              title="Affiliate List Management"
              maxWidth="md"
            >
              <ViewAffiliates
                accountName={getValues("CustomerName")}
                customerNum={getValues("CustomerNum")}
              />
            </Modal>
          </>
        )}

      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <Grid
            container
            spacing={1}
            direction="row"
            sx={{ height: `calc(100vh - 112px)`, alignItems: "center" }}
          >
            <Grid
              container
              spacing={1}
              size={12}
              sx={{
                border: "1px solid lightgrey",
                padding: "20px",
                borderRadius: "15px",
                boxShadow: "0 1px 8px rgba(0, 0, 0, 0.25)",
                backgroundColor: "#EBF0F8",
              }}
            >
              <Grid size={{ xs: 12, md: 3 }}>
                <FormControl fullWidth>
                  <InputLabel>Account Status</InputLabel>
                  <Controller
                    name="AcctStatus"
                    control={control}
                    disabled={!isEnabled("AcctStatus")}
                    render={({ field }) => (
                      <Select
                        {...field}
                        label="Account Status"
                        value={accountStatus}
                        onChange={(e) => {
                          setAccountStatus(e.target.value);
                          setValue("AcctStatus", e.target.value);
                          if (e.target.value !== "Inactive") {
                            setValue("DateNotif", "");
                            setValue("TermDate", "");
                            setValue("TermCode", "");
                          }
                        }}
                      >
                        <MenuItem value="Active">Active</MenuItem>
                        <MenuItem value="Inactive">Inactive</MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <Controller
                  name="CustomerName"
                  control={control}
                  disabled={!isEnabled("CustomerName")}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Special Account Name"
                      required
                    />
                  )}
                />
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <Controller
                  name="CustomerNum"
                  control={control}
                  disabled={!isEnabled("CustomerNum")}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Cust #" required />
                  )}
                />
              </Grid>

              <Grid
                size={{
                  xs: 12,
                  md:
                    pathname !== "/sac-create-new-account" &&
                    state?.from !== "/pending-items"
                      ? 3
                      : 4,
                }}
              >
                <FormControl fullWidth>
                  <InputLabel>SAC 1</InputLabel>
                  <Controller
                    name="SAC_Contact1"
                    control={control}
                    disabled={!isEnabled("SAC_Contact1")}
                    render={({ field }) => (
                      <Select {...field} label="SAC 1">
                        <MenuItem value="Marc De Luca">Marc De Luca</MenuItem>
                        <MenuItem value="Sharon Carruth">
                          Sharon Carruth
                        </MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>
              <Grid
                size={{
                  xs: 12,
                  md:
                    pathname !== "/sac-create-new-account" &&
                    state?.from !== "/pending-items"
                      ? 3
                      : 4,
                }}
              >
                <FormControl fullWidth>
                  <InputLabel>Risk Solutions 1</InputLabel>
                  <Controller
                    name="LossCtlRep1"
                    control={control}
                    disabled={!isEnabled("LossCtlRep1")}
                    render={({ field }) => (
                      <Select {...field} label="Risk Solutions 1">
                        <MenuItem value="Robert Boutin">Robert Boutin</MenuItem>
                        <MenuItem value="Richelle Chandler">
                          Richelle Chandler
                        </MenuItem>
                        <MenuItem value="Shawn Barry">Shawn Barry</MenuItem>
                        <MenuItem value="Non-Renewed">Non-Renewed</MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>
              <Grid
                size={{
                  xs: 12,
                  md:
                    pathname !== "/sac-create-new-account" &&
                    state?.from !== "/pending-items"
                      ? 1.5
                      : 4,
                }}
              >
                <Controller
                  name="DateCreated"
                  control={control}
                  disabled={!isEnabled("DateCreated")}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Created Date"
                      type="date"
                      InputLabelProps={{ shrink: true }}
                    />
                  )}
                />
              </Grid>
              {pathname !== "/sac-create-new-account" &&
                state?.from !== "/pending-items" && (
                  <Grid size={{ xs: 12, md: 4.5 }}>
                    <FormControl fullWidth>
                      <InputLabel>
                        Does this customer account have other related special
                        accounts entities?
                      </InputLabel>
                      <Controller
                        name="RelatedEnt"
                        control={control}
                        disabled={!isEnabled("RelatedEnt")}
                        render={({ field }) => (
                          <Select
                            {...field}
                            label="Does this customer account have other related special accounts entities?"
                            value={haveOtherRelatedAccounts}
                            onChange={(e) => {
                              setHaveOtherRelatedAccounts(e.target.value);
                              setValue("RelatedEnt", e.target.value);
                            }}
                          >
                            <MenuItem value="Yes">Yes</MenuItem>
                            <MenuItem value="No">No</MenuItem>
                          </Select>
                        )}
                      />
                    </FormControl>
                  </Grid>
                )}

              <Grid size={{ xs: 12, md: 3 }}>
                <FormControl fullWidth>
                  <InputLabel>SAC 2</InputLabel>
                  <Controller
                    name="SAC_Contact2"
                    control={control}
                    disabled={!isEnabled("SAC_Contact2")}
                    render={({ field }) => (
                      <Select {...field} label="SAC 2">
                        <MenuItem value="Jenna Houle">Jenna Houle</MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <FormControl fullWidth>
                  <InputLabel>Risk Solutions 2</InputLabel>
                  <Controller
                    name="LossCtlRep2"
                    control={control}
                    disabled={!isEnabled("LossCtlRep2")}
                    render={({ field }) => (
                      <Select {...field} label="Risk Solutions 2">
                        <MenuItem value="Robert Boutin">Robert Boutin</MenuItem>
                        <MenuItem value="Richelle Chandler">
                          Richelle Chandler
                        </MenuItem>
                        <MenuItem value="Shawn Barry">Shawn Barry</MenuItem>
                        <MenuItem value="Non-Renewed">Non-Renewed</MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <Controller
                  name="OnBoardDate"
                  control={control}
                  disabled={!isEnabled("OnBoardDate")}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="On Board Date"
                      type="date"
                      InputLabelProps={{ shrink: true }}
                      required
                    />
                  )}
                />
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <Controller
                  name="DateNotif"
                  control={control}
                  disabled={
                    !isEnabled("DateNotif") || accountStatus !== "Inactive"
                  }
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Notification Date"
                      type="date"
                      InputLabelProps={{ shrink: true }}
                      required
                    />
                  )}
                />
              </Grid>

              <Grid size={{ xs: 12, md: 3 }}>
                <FormControl fullWidth>
                  <InputLabel>Acct Owner</InputLabel>
                  <Controller
                    name="AcctOwner"
                    control={control}
                    disabled={!isEnabled("AcctOwner")}
                    render={({ field }) => (
                      <Select {...field} label="Acct Owner">
                        <MenuItem value="Marc De Luca">Marc De Luca</MenuItem>
                        <MenuItem value="Sharon Carruth">
                          Sharon Carruth
                        </MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <FormControl fullWidth>
                  <InputLabel>Risk Mgr</InputLabel>
                  <Controller
                    name="RiskSolMgr"
                    control={control}
                    disabled={!isEnabled("RiskSolMgr")}
                    render={({ field }) => (
                      <Select {...field} label="Risk Mgr">
                        <MenuItem value="David Partain">David Partain</MenuItem>
                        <MenuItem value="Tarek Helwani">Tarek Helwani</MenuItem>
                        <MenuItem value="Carol Hanover">Carol Hanover</MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <FormControl fullWidth>
                  <InputLabel>On Board Method</InputLabel>
                  <Controller
                    name="OBMethod"
                    control={control}
                    disabled={!isEnabled("OBMethod")}
                    render={({ field }) => (
                      <Select {...field} label="On Board Method">
                        <MenuItem value="Remote">Remote</MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <Controller
                  name="TermDate"
                  control={control}
                  disabled={
                    !isEnabled("TermDate") || accountStatus !== "Inactive"
                  }
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Termination Date"
                      type="date"
                      InputLabelProps={{ shrink: true }}
                      required
                    />
                  )}
                />
              </Grid>

              {/* <Grid size={{ xs: 12, md: 3 }}>
                <FormControl fullWidth>
                  <InputLabel>Created By</InputLabel>
                  <Controller
                    name="CreatedBy"
                    control={control}
                    disabled={!isEnabled("CreatedBy")}
                    render={({ field }) => (
                      <Select {...field} label="Created By">
                        <MenuItem value="DEBORAH G.BELLINA">
                          DEBORAH G.BELLINA
                        </MenuItem>
                        <MenuItem value="Michelle Bond">Michelle Bond</MenuItem>
                        <MenuItem value="Patricia Lewis">
                          Patricia Lewis
                        </MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid> */}
              <Grid size={{ xs: 12, md: 4 }}>
                <FormControl fullWidth>
                  <InputLabel required>Branch Name</InputLabel>
                  <Controller
                    name="BranchName"
                    control={control}
                    disabled={!isEnabled("BranchName")}
                    render={({ field }) => (
                      <Select {...field} label="Branch Name" required>
                        <MenuItem value="West - 04 - Louisiana Branch">
                          West - 04 - Louisiana Branch
                        </MenuItem>
                        <MenuItem value="Midwest - 13 - Illinois Branch">
                          Midwest - 13 - Illinois Branch
                        </MenuItem>
                        <MenuItem value="Northeast - 32 - Massachusetts Branch">
                          Northeast - 32 - Massachusetts Branch
                        </MenuItem>
                        <MenuItem value="Northeast - 41 - New Jersey Branch">
                          Northeast - 41 - New Jersey Branch
                        </MenuItem>
                        <MenuItem value="Southeast - 18 - Tennessee Branch">
                          Southeast - 18 - Tennessee Branch
                        </MenuItem>
                        <MenuItem value="Pacific - 10 - Southern California Branch">
                          Pacific - 10 - Southern California Branch
                        </MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <FormControl fullWidth>
                  <InputLabel>Market Segmentation</InputLabel>
                  <Controller
                    name="MarketSegmentation"
                    control={control}
                    disabled={!isEnabled("MarketSegmentation")}
                    render={({ field }) => (
                      <Select {...field} label="Market Segmentation">
                        <MenuItem value="demo">demo</MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <FormControl fullWidth>
                  <InputLabel required>Termination Reason</InputLabel>
                  <Controller
                    name="TermCode"
                    control={control}
                    disabled={
                      !isEnabled("TermCode") || accountStatus !== "Inactive"
                    }
                    render={({ field }) => (
                      <Select {...field} label="Termination Reason">
                        <MenuItem value="Unknown">Unknown</MenuItem>
                        <MenuItem value="Competitive Pricing">
                          Competitive Pricing
                        </MenuItem>
                        <MenuItem value="Underwriting Decision">
                          Underwriting Decision
                        </MenuItem>
                        <MenuItem value="Deductible Billing Moved to Paragon">
                          Deductible Billing Moved to Paragon
                        </MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>

              <Grid size={{ xs: 12, md: 12 }}>
                <Controller
                  name="AccountNotes"
                  control={control}
                  disabled={!isEnabled("AccountNotes")}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Account Details"
                      multiline
                      rows={4}
                    />
                  )}
                />
              </Grid>
              {haveOtherRelatedAccounts === "Yes" && (
                <Grid size={{ xs: 12, md: 12 }} sx={{ textAlign: "center" }}>
                  <Typography variant="body1" color="red">
                    This Customer Account Has Other Related Special Account
                    Entities
                  </Typography>
                </Grid>
              )}
            </Grid>

            <Box
              sx={{
                width: "100%",
                border: "1px solid lightgrey",
                padding: "20px 20px 10px 20px",
                borderRadius: "15px",
                boxShadow: "0 1px 8px rgba(0, 0, 0, 0.25)",
              }}
            >
              <Tabs
                value={tabIndex}
                onChange={handleTabChange}
                variant="scrollable"
                scrollButtons="auto"
                aria-label="account tabs"
                sx={{ mb: 1.5, ".MuiTabs-indicator": { display: "none" } }}
              >
                <Tab
                  label="Account Service"
                  sx={{
                    borderRadius: "50px",
                    backgroundColor: "#EBF0F8",
                    mr: 1.5,
                    "&.Mui-selected": {
                      color: "white",
                      background:
                        "linear-gradient(90deg, hsla(303, 77%, 22%, 1) 0%, hsla(321, 55%, 50%, 1) 100%)",
                    },
                  }}
                />
                {/* <Tab
                  label="Stewardship"
                  sx={{ borderRadius: '50px', backgroundColor: '#EBF0F8', mr: 1.5, '&.Mui-selected': { color: 'white', background: 'linear-gradient(90deg, hsla(303, 77%, 22%, 1) 0%, hsla(321, 55%, 50%, 1) 100%)' } }}
                /> */}
                <Tab
                  label="NCM"
                  sx={{
                    borderRadius: "50px",
                    backgroundColor: "#EBF0F8",
                    mr: 1.5,
                    "&.Mui-selected": {
                      color: "white",
                      background:
                        "linear-gradient(90deg, hsla(303, 77%, 22%, 1) 0%, hsla(321, 55%, 50%, 1) 100%)",
                    },
                  }}
                />
                <Tab
                  label="Loss Run Scheduling"
                  sx={{
                    borderRadius: "50px",
                    backgroundColor: "#EBF0F8",
                    mr: 1.5,
                    "&.Mui-selected": {
                      color: "white",
                      background:
                        "linear-gradient(90deg, hsla(303, 77%, 22%, 1) 0%, hsla(321, 55%, 50%, 1) 100%)",
                    },
                  }}
                />
                <Tab
                  label="Loss Run Notes"
                  sx={{
                    borderRadius: "50px",
                    backgroundColor: "#EBF0F8",
                    mr: 1.5,
                    "&.Mui-selected": {
                      color: "white",
                      background:
                        "linear-gradient(90deg, hsla(303, 77%, 22%, 1) 0%, hsla(321, 55%, 50%, 1) 100%)",
                    },
                  }}
                />
                <Tab
                  label="Deductible Bill"
                  sx={{
                    borderRadius: "50px",
                    backgroundColor: "#EBF0F8",
                    mr: 1.5,
                    "&.Mui-selected": {
                      color: "white",
                      background:
                        "linear-gradient(90deg, hsla(303, 77%, 22%, 1) 0%, hsla(321, 55%, 50%, 1) 100%)",
                    },
                  }}
                />
                <Tab
                  label="Claim Review Scheduling"
                  sx={{
                    borderRadius: "50px",
                    backgroundColor: "#EBF0F8",
                    mr: 1.5,
                    "&.Mui-selected": {
                      color: "white",
                      background:
                        "linear-gradient(90deg, hsla(303, 77%, 22%, 1) 0%, hsla(321, 55%, 50%, 1) 100%)",
                    },
                  }}
                />
                <Tab
                  label="Claim Review Notes"
                  sx={{
                    borderRadius: "50px",
                    backgroundColor: "#EBF0F8",
                    mr: 1.5,
                    "&.Mui-selected": {
                      color: "white",
                      background:
                        "linear-gradient(90deg, hsla(303, 77%, 22%, 1) 0%, hsla(321, 55%, 50%, 1) 100%)",
                    },
                  }}
                />
                <Tab
                  label="SHI"
                  sx={{
                    borderRadius: "50px",
                    backgroundColor: "#EBF0F8",
                    mr: 1.5,
                    "&.Mui-selected": {
                      color: "white",
                      background:
                        "linear-gradient(90deg, hsla(303, 77%, 22%, 1) 0%, hsla(321, 55%, 50%, 1) 100%)",
                    },
                  }}
                />
                <Tab
                  label="Change Notes"
                  sx={{
                    borderRadius: "50px",
                    backgroundColor: "#EBF0F8",
                    mr: 1.5,
                    "&.Mui-selected": {
                      color: "white",
                      background:
                        "linear-gradient(90deg, hsla(303, 77%, 22%, 1) 0%, hsla(321, 55%, 50%, 1) 100%)",
                    },
                  }}
                />
              </Tabs>

              <TabPanel value={tabIndex} index={0}>
                <AccountService isEnabled={isEnabled} />
              </TabPanel>
              {/* <TabPanel value={tabIndex} index={1}>
                Stewardship.
              </TabPanel> */}
              <TabPanel value={tabIndex} index={1}>
                <NcmTab isEnabled={isEnabled} />
              </TabPanel>
              <TabPanel value={tabIndex} index={2}>
                <LossRunScheduling isEnabled={isEnabled} />
              </TabPanel>
              <TabPanel value={tabIndex} index={3}>
                <Notes
                  name="LossRunNotes"
                  label="Loss Run Notes"
                  isEnabled={isEnabled}
                />
              </TabPanel>
              <TabPanel value={tabIndex} index={4}>
                <DeductibleBill isEnabled={isEnabled} />
              </TabPanel>
              <TabPanel value={tabIndex} index={5}>
                <ClaimReviewScheduling isEnabled={isEnabled} />
              </TabPanel>
              <TabPanel value={tabIndex} index={6}>
                <Notes
                  name="ClaimRevNotes"
                  label="Claim Review Notes"
                  isEnabled={isEnabled}
                />
              </TabPanel>
              <TabPanel value={tabIndex} index={7}>
                <Shi isEnabled={isEnabled} />
              </TabPanel>
              <TabPanel value={tabIndex} index={8}>
                <Notes
                  name="ChangeNotes"
                  label="Change Notes"
                  isEnabled={isEnabled}
                />
              </TabPanel>
            </Box>

            <Grid
              sx={{
                width: "100%",
                display: "flex",
                justifyContent: "space-between",
              }}
            >
              <Grid
                sx={{
                  display: "flex",
                  gap: 2,
                }}
              >
                {pathname !== "/sac-create-new-account" &&
                  state?.from !== "/pending-items" && (
                    <>
                      <Button
                        variant="outlined"
                        color="primary"
                        onClick={() => setViewPolicies(true)}
                        // disabled
                        sx={{ height: 45, width: 200 }}
                      >
                        View Policies
                      </Button>
                      <Button
                        variant="outlined"
                        color="primary"
                        onClick={() => setViewAffiliates(true)}
                        // disabled
                        sx={{ height: 45, width: 200 }}
                      >
                        View Affiliates
                      </Button>
                    </>
                  )}
              </Grid>
              <Grid
                sx={{
                  height: "40px",
                  display: "flex",
                  gap: 2,
                }}
              >
                <Button
                  type="button"
                  variant="outlined"
                  onClick={handleCancel}
                  disabled={submitOrSave !== ""}
                  sx={{ height: 45, width: 90 }}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="outlined"
                  color="primary"
                  name="save"
                  disabled={submitOrSave !== ""}
                  sx={{ height: 45, width: 90 }}
                >
                  {submitOrSave === "save" ? (
                    <CircularProgress size={20} color="inherit" />
                  ) : (
                    "Save"
                  )}
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  name="submit"
                  disabled={submitOrSave !== ""}
                  sx={{ height: 45, width: 90 }}
                >
                  {submitOrSave === "submit" ? (
                    <CircularProgress size={20} color="inherit" />
                  ) : (
                    "Submit"
                  )}
                </Button>
              </Grid>
            </Grid>
          </Grid>
        </form>
      </FormProvider>
    </>
  );
};

export default SacCreateNewAccount;
