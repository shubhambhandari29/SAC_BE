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
  useTheme,
  CircularProgress,
} from "@mui/material";
import { useEffect, useState } from "react";
import { useForm, Controller, FormProvider } from "react-hook-form";
import {
  useLocation,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import Policy from "./Policy";
import InsuredContacts from "./InsuredContacts";
import ClaimHandling1 from "./ClaimHandling1";
import ClaimHandling2 from "./ClaimHandling2";
import ClaimHandling3 from "./ClaimHandling3";
import CctInstructionsOther from "./CctInstructionsOther";
import Agent from "./Agent";
import CctInstructionsPolicy from "./CctInstructionsPolicy";
import CctAssignment from "./CctAssignment";
import TabPanel from "../../../../ui/TabPanel";
import api from "../../../../../api/api";
import Loader from "../../../../ui/Loader";
import Deductible from "./Deductible";
import Swal from "sweetalert2";
import ShiPrint from "../../../ShiPrint";
import { policyFieldPermissions } from "../../../../../field-permissions";
import { useSelector } from "react-redux";

const defaultValues = {
  PolPref: "",
  PolicyNum: "",
  PolMod: "",
  AccountName: "",
  CustomerNum: "",
  AcctOnPolicyName: "",
  // GroupCode: "",
  PolicyStatus: "",
  LocList: "",
  LocCoded: "",
  InceptDate: "",
  LocCompDate: "",
  ExpDate: "",
  PolicyType: "",
  PolicyBusinessType: "",
  PolicyNotes: "",
  //Policy
  DateCreated: new Date().toISOString().split("T")[0],
  CreatedBy: "",
  UnderwriterName: "",
  UWMgr: "",
  DNRDate: "",
  DNRStatus: "",
  RenewDiaryDT: "",
  PremiumAmt: "",
  //Agent
  AgentName: "",
  AgentCode: "",
  AgentSeg: "",
  AgentContact1: "",
  AgentTel1: "",
  AgentCell1: "",
  AgentFax1: "",
  AgentEmail1: "",
  AgentContact2: "",
  AgentTel2: "",
  AgentCell2: "",
  AgentFax2: "",
  AgentEmail2: "",
  //Insured contact
  InsuredContact1: "",
  InsuredTitle1: "",
  InsuredPhone1: "",
  InsuredCell1: "",
  InsuredFax1: "",
  InsuredEmail1: "",
  InsuredContact2: "",
  InsuredTitle2: "",
  InsuredPhone2: "",
  InsuredCell2: "",
  InsuredFax2: "",
  InsuredEmail2: "",
  InsuredNotes: "",
  //deductiable
  LargeDeductYN: "",
  BillExpYN: "",
  BillName: "",
  AggMet: "",
  AggAmt: "",
  LCFRate: "",
  LCYN: "",
  LCAmt: "",
  LCBank: "",
  PerClaimAggAmt: "",
  FeatType: "",
  SentParagon: "",
  DeductNotesOne: "",
  DeductNotesTwo: "",
  //claim handling1
  ContactInstruct: "",
  CoverageInstruct: "",
  ReserveInstruct: "",
  //claim handling2
  PrefCounselYN: "No",
  LitigationInstruct: "",
  SettlementInstruct: "",
  //claim handling3
  RecoveryInstruct: "",
  MiscCovInstruct: "",
  //cct instructions policy
  CCTBusLine: "",
  UnManPol: "",
  AutoPolYN: "",
  RentedHired: "",
  AcctProdClaims: "",
  AcctValetCov: "",
  WCCClassCodeYN: "",
  WCClassNotes: "",
  NoLocYN: "",
  NoLocNotes: "",
  //cct instructions other
  HCSSupport: "",
  AddlDocs: "",
  AcctLocID: "",
  PMSUnit: "",
  AccLocNotes: "",
  PMSUnitNotes: "",
  CCTOtherNotes: "",
  //cct assignment
  SpecHand: "Auto Assign",
  CCTAssgInstruct: "",
};

export default function CreateNewPolicy() {
  const methods = useForm({
    defaultValues,
  });
  const { handleSubmit, control, reset, setValue, getValues } = methods;
  const [tabIndex, setTabIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const { column_name } = useParams();
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [policyStatus, setPolicyStatus] = useState("");
  const { pathname, state } = useLocation();
  const from = state?.from || "/pending-items";
  const theme = useTheme();
  const [showCompDt, setShowCompDt] = useState(false);
  const [searchParams] = useSearchParams();
  const user = useSelector((state) => state.auth.user);
  const allowedFields = policyFieldPermissions[user.role];

  const isEnabled = (fieldName) => {
    if (allowedFields === "ALL") return true;
    return allowedFields?.includes(fieldName);
  };

  const tabList = [
    { label: "Policy", component: <Policy isEnabled={isEnabled} /> },
    { label: "Agent", component: <Agent isEnabled={isEnabled} /> },
    {
      label: "Insured Contacts",
      component: <InsuredContacts isEnabled={isEnabled} />,
    },
    { label: "Deductible", component: <Deductible isEnabled={isEnabled} /> },
    {
      label: "Claim Handling (1)",
      component: <ClaimHandling1 isEnabled={isEnabled} />,
    },
    {
      label: "Claim Handling (2)",
      component: <ClaimHandling2 isEnabled={isEnabled} />,
    },
    {
      label: "Claim Handling (3)",
      component: <ClaimHandling3 isEnabled={isEnabled} />,
    },
    {
      label: "CCT Instructions Policy",
      component: <CctInstructionsPolicy isEnabled={isEnabled} />,
    },
    {
      label: "CCT Instructions Other",
      component: <CctInstructionsOther isEnabled={isEnabled} />,
    },
    {
      label: "CCT Assignment",
      component: <CctAssignment isEnabled={isEnabled} />,
    },
    { label: "Shi Print", component: <ShiPrint isEnabled={isEnabled} /> },
  ];

  const onSubmit = async (data, e) => {
    const filteredData = Object.fromEntries(
      Object.entries(data).filter(([_, v]) => v !== null && v !== "")
    );

    //confirmation alert on submission
    const confirmRes = await Swal.fire({
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
    if (confirmRes.dismiss === Swal.DismissReason.cancel) return;

    setSubmitting(true);

    try {
      const res = await api.post("/sac_policies/upsert", { ...filteredData });
      if (res.status === 200) {
        await Swal.fire({
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

        setSubmitting(false);
        if (pathname.includes("create-new-policy")) {
          navigate(`/view-policy/PK_Number=${res.data.PK_Number}`, {
            state: { from },
            replace: true,
          });
        }
      }
      // reset(defaultValues);
    } catch (err) {
      console.error(err);
      //implement error handling
    } finally {
      setSubmitting(false);
    }
  };

  const handleTabChange = (_, newValue) => setTabIndex(newValue);

  useEffect(() => {
    if (searchParams.size === 2) {
      reset({
        ...defaultValues,
        CustomerNum: searchParams.get("CustomerNum"),
        AccountName: searchParams.get("CustomerName"),
      });
      return;
    }

    if (!column_name) {
      reset(defaultValues);
      return;
    }

    const fetchData = async (searchByColumn, value) => {
      try {
        setLoading(true);
        const res = await api.get("/sac_policies/", {
          params: { [searchByColumn]: value },
        });

        //replacing all null values with empty string
        const data = Object.fromEntries(
          Object.entries(res.data[0]).map(([k, v]) => [k, v === null ? "" : v])
        );

        let formattedData = {
          ...data,
          InceptDate: data.InceptDate ? data.InceptDate.split("T")[0] : "",
          LocCompDate: data.LocCompDate ? data.LocCompDate.split("T")[0] : "",
          ExpDate: data.ExpDate ? data.ExpDate.split("T")[0] : "",
          DateCreated: data.DateCreated ? data.DateCreated.split("T")[0] : "",
          DNRDate: data.DNRDate ? data.DNRDate.split("T")[0] : "",
          RenewDiaryDT: data.RenewDiaryDT
            ? data.RenewDiaryDT.split("T")[0]
            : "",
          PolMod: from.includes("view-policy")
            ? parseInt(data.PolMod) + 1
            : data.PolMod,
        };

        setPolicyStatus(formattedData.PolicyStatus);
        reset(formattedData);
      } catch (err) {
        console.error("Error fetching data", err);
      } finally {
        setLoading(false);
      }
    };

    const [key, value] = column_name.split("=");
    fetchData(key, value);
  }, [column_name, reset, from, searchParams]);

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

    if (res.isConfirmed)
      navigate(from, { state: { from: pathname }, replace: true });
  };

  const handlePolicyStatus = (e) => {
    setPolicyStatus(e.target.value);
    setValue("PolicyStatus", e.target.value);

    if (e.target.value === "Pending Renewal") {
      setValue("PolicyBusinessType", "Renewal Business");
      setValue("UnManPol", "1");
    } else setValue("UnManPol", "2");

    if (
      e.target.value === "Canceled" ||
      e.target.value === "Canceled - Mod Bump" ||
      e.target.value === "Canceled - Rewrite" ||
      e.target.value === "Non-Renewal"
    ) {
      setShowCompDt(true);
      setValue("LocCompDate", new Date().toISOString().split("T")[0]);
    }

    if (
      e.target.value === "Active" ||
      e.target.value === "Cancellation Pending" ||
      e.target.value === "Expired Mod" ||
      e.target.value === "Fronted Policy - Not Hanover Paper" ||
      e.target.value === "New Business - Not in PMS Yet" ||
      e.target.value === "Pending Renewal" ||
      e.target.value === "Runoff"
    ) {
      setShowCompDt(false);
      setValue("LocCompDate", "");
    }
  };

  if (loading) return <Loader size={40} height="800px" />;

  return (
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
            <Grid size={{ xs: 12, md: 1 }}>
              <Controller
                name="PolPref"
                control={control}
                disabled={!isEnabled("PolPref")}
                render={({ field }) => (
                  <TextField {...field} fullWidth label="Prefix" />
                )}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <Controller
                name="PolicyNum"
                control={control}
                disabled={!isEnabled("PolicyNum")}
                render={({ field }) => (
                  <TextField {...field} fullWidth label="Policy #" />
                )}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 1 }}>
              <Controller
                name="PolMod"
                control={control}
                disabled={!isEnabled("PolMod")}
                render={({ field }) => (
                  <TextField {...field} fullWidth label="Mod" />
                )}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 7 }}>
              <Controller
                name="AccountName"
                control={control}
                disabled={!isEnabled("AccountName")}
                render={({ field }) => (
                  <TextField {...field} fullWidth label="Customer Name" />
                )}
              />
            </Grid>

            <Grid size={{ xs: 12, md: 5 }}>
              <Controller
                name="CustomerNum"
                control={control}
                disabled={!isEnabled("CustomerNum")}
                render={({ field }) => (
                  <TextField {...field} fullWidth label="Customer #" />
                )}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 7 }}>
              <Controller
                name="AcctOnPolicyName"
                control={control}
                disabled={!isEnabled("AcctOnPolicyName")}
                render={({ field }) => (
                  <TextField {...field} fullWidth label="Policy Name Insured" />
                )}
              />
            </Grid>

            {/* <Grid size={{ xs: 12, md: 3 }}>
              <FormControl fullWidth>
                <InputLabel>Group Code</InputLabel>
                <Controller
                  name="GroupCode"
                  control={control}
                  disabled={!isEnabled("GroupCode")}
                  render={({ field }) => (
                    <Select {...field} label="Group Code">
                      <MenuItem value="XXX">XXX</MenuItem>
                      <MenuItem value="ZCK">ZCK</MenuItem>
                      <MenuItem value="ZJA">ZJA</MenuItem>
                    </Select>
                  )}
                />
              </FormControl>
            </Grid> */}
            <Grid size={{ xs: 12, md: 4 }}>
              <FormControl fullWidth>
                <InputLabel>Policy Status</InputLabel>
                <Controller
                  name="PolicyStatus"
                  control={control}
                  disabled={!isEnabled("PolicyStatus")}
                  render={({ field }) => (
                    <Select
                      {...field}
                      label="Policy Status"
                      onChange={handlePolicyStatus}
                      value={policyStatus}
                    >
                      <MenuItem value="Active">Active</MenuItem>
                      <MenuItem value="Expired Mod">Expired Mod</MenuItem>
                      <MenuItem value="Pending Renewal">
                        Pending Renewal
                      </MenuItem>
                      <MenuItem value="Non-Renewal">Non-Renewal</MenuItem>
                      <MenuItem value="Cancellation Pending">
                        Cancellation Pending
                      </MenuItem>
                      <MenuItem value="Canceled">Canceled</MenuItem>
                      <MenuItem value="Canceled - Rewrite">
                        Canceled - Rewrite
                      </MenuItem>
                      <MenuItem value="Canceled - Mod Bump">
                        Canceled - Mod Bump
                      </MenuItem>
                      <MenuItem value="Fronted Policy - Not Hanover Paper">
                        Fronted Policy - Not Hanover Paper
                      </MenuItem>
                      <MenuItem value="New Business - Not in PMS Yet">
                        New Business - Not in PMS Yet
                      </MenuItem>
                      <MenuItem value="Runoff">Runoff</MenuItem>
                    </Select>
                  )}
                />
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <FormControl fullWidth>
                <InputLabel>Location List</InputLabel>
                <Controller
                  name="LocList"
                  control={control}
                  disabled={!isEnabled("LocList")}
                  render={({ field }) => (
                    <Select {...field} label="Location List">
                      <MenuItem value="">N/A</MenuItem>
                      <MenuItem value="Completed">Completed</MenuItem>
                    </Select>
                  )}
                />
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <FormControl fullWidth>
                <InputLabel>Is Location Coded?</InputLabel>
                <Controller
                  name="LocCoded"
                  control={control}
                  disabled={!isEnabled("LocCoded")}
                  render={({ field }) => (
                    <Select {...field} label="Is Location Coded?">
                      <MenuItem value="Yes">Yes</MenuItem>
                      <MenuItem value="No">No</MenuItem>
                    </Select>
                  )}
                />
              </FormControl>
            </Grid>

            <Grid size={{ xs: 12, md: 4 }}>
              <Controller
                name="InceptDate"
                control={control}
                disabled={!isEnabled("InceptDate")}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Inception Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                  />
                )}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <Controller
                name="LocCompDate"
                control={control}
                disabled={!isEnabled("LocCompDate")}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Location Completion Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    disabled={!showCompDt}
                  />
                )}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <Controller
                name="ExpDate"
                control={control}
                disabled={!isEnabled("ExpDate")}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Expiration Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                  />
                )}
              />
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Policy Type</InputLabel>
                <Controller
                  name="PolicyType"
                  control={control}
                  disabled={!isEnabled("PolicyType")}
                  render={({ field }) => (
                    <Select {...field} label="Policy Type">
                      <MenuItem value="Commercial Auto">
                        Commercial Auto
                      </MenuItem>
                      <MenuItem value="Commercial Package">
                        Commercial Package
                      </MenuItem>
                      <MenuItem value="GarageKeepers">GarageKeepers</MenuItem>
                      <MenuItem value="General Liability">
                        General Liability
                      </MenuItem>
                      <MenuItem value="Umbrella">Umbrella</MenuItem>
                      <MenuItem value="Workers Compensation">
                        Workers Compensation
                      </MenuItem>
                    </Select>
                  )}
                />
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Policy Business Status</InputLabel>
                <Controller
                  name="PolicyBusinessType"
                  control={control}
                  disabled={!isEnabled("PolicyBusinessType")}
                  render={({ field }) => (
                    <Select {...field} label="Policy Business Status">
                      <MenuItem value="New Business">New Business</MenuItem>
                      <MenuItem value="Non Renewed Business">
                        Non Renewed Business
                      </MenuItem>
                      <MenuItem value="Prior to SAC">Prior to SAC</MenuItem>
                      <MenuItem value="Renewal Business">
                        Renewal Business
                      </MenuItem>
                    </Select>
                  )}
                />
              </FormControl>
            </Grid>

            <Grid size={{ xs: 12, md: 12 }}>
              <Controller
                name="PolicyNotes"
                control={control}
                disabled={!isEnabled("PolicyNotes")}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Notes"
                    multiline
                    rows={3}
                  />
                )}
              />
            </Grid>
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
              {tabList.map((tab) => (
                <Tab
                  key={tab.label}
                  label={tab.label}
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
              ))}
            </Tabs>

            {tabList.map((tab, i) => (
              <TabPanel key={i} value={tabIndex} index={i}>
                {tab.component}
              </TabPanel>
            ))}
          </Box>

          <Grid
            sx={{
              width: "100%",
              display: "flex",
              justifyContent: "space-between",
            }}
          >
            <Grid container spacing={2}>
              {pathname !== "/create-new-policy" && (
                <>
                  <Button
                    variant="outlined"
                    color="primary"
                    onClick={() =>
                      navigate(
                        `/create-new-policy?CustomerNum=${getValues(
                          "CustomerNum"
                        )}&CustomerName=${getValues("AccountName")}`,
                        { state: { from }, replace: true }
                      )
                    }
                    sx={{ height: 45, width: 280 }}
                  >
                    Create a Brand New Policy
                  </Button>
                  <Button
                    variant="outlined"
                    color="primary"
                    onClick={() => {
                      navigate(
                        `/view-policy/PK_Number=${
                          column_name.split("=")[1]
                        }?nextMod=true`,
                        { state: { from }, replace: true }
                      );
                    }}
                    sx={{ height: 45, width: 280 }}
                  >
                    Create Next Mod on Same Policy
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
                disabled={submitting}
                sx={{ height: 45, width: 90 }}
              >
                Cancel
              </Button>
              {/* <Button
                type="submit"
                variant="outlined"
                color="primary"
                name="save"
                disabled={submitting}
                sx={{ height: 45, width: 90 }}
              >
                {submitting ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  "Save"
                )}
              </Button> */}
              <Button
                type="submit"
                variant="contained"
                color="primary"
                name="submit"
                disabled={submitting}
                sx={{ height: 45, width: 90 }}
              >
                {submitting ? (
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
  );
}
