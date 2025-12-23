import { useState, useEffect } from "react";
import {
  useForm,
  FormProvider,
  useFieldArray,
  Controller,
} from "react-hook-form";
import { DataGrid } from "@mui/x-data-grid";
import {
  Button,
  IconButton,
  TextField,
  Typography,
  Select,
  MenuItem,
  useTheme,
} from "@mui/material";
import { MdOutlineCancel } from "react-icons/md";
import api from "../../../../api/api";
import Loader from "../../../ui/Loader";
import Swal from "sweetalert2";
import useDropdownData from "../../../../hooks/useDropdownData";

export default function ReportRecipientList({ url, parameter }) {
  const [isEdit, setIsEdit] = useState(false);
  const [originalData, setOriginalData] = useState([]);
  const methods = useForm({
    defaultValues: {
      recipients: [],
    },
  });
  const [loading, setLoading] = useState("");
  const [deleted, setDeleted] = useState([]);
  const { control, handleSubmit, reset } = methods;
  const { fields, append, remove, replace } = useFieldArray({
    control,
    name: "recipients",
  });
  const theme = useTheme();
  const { data: ddData, loading: ddLoading } =
    useDropdownData("/dropdowns/all");

  useEffect(() => {
    const fetchData = async () => {
      setLoading("fetching");
      try {
        const res = await api.get(url, {
          params: parameter,
        });
        setOriginalData(res.data);
        reset({ recipients: res.data });
      } catch (err) {
        console.error("Failed to fetch recipients:", err);
      } finally {
        setLoading("");
      }
    };
    fetchData();
  }, [reset, url, parameter]);

  const onSubmit = (data) => {
    let dataValidationError;
    data.recipients.forEach((r) => {
      dataValidationError =
        !r[Object.keys(parameter)[0]] ||
        !r.RecipCat ||
        !r.DistVia ||
        !r.AttnTo ||
        !r.EMailAddress;
    });

    //data validation alert when mandatory fields are missing
    if (dataValidationError) {
      Swal.fire({
        title: "Data Validation Error",
        text: `You've left blank a mandatory field. Please check your entries.`,
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

    // Remove empty new rows
    let filteredList = data.recipients.filter(
      (r) =>
        r[Object.keys(parameter)[0]].trim() ||
        r.RecipCat.trim() ||
        r.DistVia.trim() ||
        r.AttnTo.trim() ||
        r.EMailAddress.trim()
    );

    if (deleted.length)
      filteredList = filteredList.filter((a1) =>
        deleted.some((a2) => a2.EMailAddress !== a1.EMailAddress)
      );

    // Check if data is same as original
    const isSame =
      JSON.stringify(filteredList) === JSON.stringify(originalData);

    if (isSame) {
      reset({ recipients: filteredList });
      setIsEdit(false);
      return;
    }

    try {
      setLoading("submitting");
      if (deleted.length) api.post(`${url}delete`, deleted);
      api.post(`${url}upsert`, filteredList);
    } catch (err) {
      console.log(err);
    } finally {
      setLoading("");
    }

    setOriginalData(filteredList);
    reset({ recipients: filteredList });
    setIsEdit(false);
  };

  const handleAdd = () => {
    append({
      [Object.keys(parameter)[0]]: Object.values(parameter)[0],
      RecipCat: "",
      DistVia: "",
      AttnTo: "",
      EMailAddress: "",
    });
  };

  const handleCancel = () => {
    setIsEdit(false);
    replace(originalData);
  };

  const columns = [
    {
      field: Object.keys(parameter)[0],
      headerName: (
        <b>
          {Object.keys(parameter)[0].replace(/([a-z])([A-Z])/g, "$1 $2")}
          <sup style={{ color: "red" }}>*</sup>
        </b>
      ),
      flex: 2,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`recipients.${params.row.rhfIndex}.${
              Object.keys(parameter)[0]
            }`}
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                sx={{ m: "5px 0px" }}
                onKeyDown={(event) => event.stopPropagation()}
              />
            )}
          />
        ) : (
          params.value
        ),
    },
    {
      field: "RecipCat",
      headerName: (
        <b>
          Recipient Category<sup style={{ color: "red" }}>*</sup>
        </b>
      ),
      flex: 1.5,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`recipients.${params.row.rhfIndex}.RecipCat`}
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                fullWidth
                sx={{ height: 40 }}
                MenuProps={{
                  PaperProps: { sx: { maxHeight: 300 } },
                }}
              >
                {ddLoading ? (
                  <MenuItem disabled>
                    <Loader size={15} height="20px" />
                  </MenuItem>
                ) : (
                  ddData
                    .filter((i) => i.DD_Type === "RecipCat")
                    .sort((a, b) => a - b)
                    .map((i) => (
                      <MenuItem key={i.DD_Value} value={i.DD_Value}>
                        {i.DD_Value}
                      </MenuItem>
                    ))
                )}
              </Select>
            )}
          />
        ) : (
          params.value
        ),
    },
    {
      field: "DistVia",
      headerName: (
        <b>
          Distribute Via<sup style={{ color: "red" }}>*</sup>
        </b>
      ),
      flex: 0.8,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`recipients.${params.row.rhfIndex}.DistVia`}
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                fullWidth
                sx={{ height: 40 }}
                MenuProps={{
                  PaperProps: { sx: { maxHeight: 300 } },
                }}
              >
                {ddLoading ? (
                  <MenuItem disabled>
                    <Loader size={15} height="20px" />
                  </MenuItem>
                ) : (
                  ddData
                    .filter((i) => i.DD_Type === "DistVia")
                    .sort((a, b) => a - b)
                    .map((i) => (
                      <MenuItem key={i.DD_Value} value={i.DD_Value}>
                        {i.DD_Value}
                      </MenuItem>
                    ))
                )}
              </Select>
            )}
          />
        ) : (
          params.value
        ),
    },
    {
      field: "AttnTo",
      headerName: (
        <b>
          Send to Attention<sup style={{ color: "red" }}>*</sup>
        </b>
      ),
      flex: 1,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`recipients.${params.row.rhfIndex}.AttnTo`}
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                sx={{ m: "5px 0px" }}
                onKeyDown={(event) => event.stopPropagation()}
              />
            )}
          />
        ) : (
          params.value
        ),
    },
    {
      field: "EMailAddress",
      headerName: (
        <b>
          E-Mail Address<sup style={{ color: "red" }}>*</sup>
        </b>
      ),
      flex: 1.5,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`recipients.${params.row.rhfIndex}.EMailAddress`}
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                sx={{ m: "5px 0px" }}
                onKeyDown={(event) => event.stopPropagation()}
              />
            )}
          />
        ) : (
          params.value
        ),
    },
    {
      field: "actions",
      headerName: "",
      flex: 0.4,
      sortable: false,
      renderCell: (params) =>
        isEdit ? (
          <IconButton
            onClick={() => {
              remove(params.row.rhfIndex);
              setDeleted((prev) => [...prev, params.row]);
            }}
          >
            <MdOutlineCancel />
          </IconButton>
        ) : null,
    },
  ];

  return (
    <FormProvider {...methods}>
      {loading === "fetching" ? (
        <Loader size={40} height="600px" />
      ) : (
        <form>
          {fields.length === 0 ? (
            <Typography
              variant="h6"
              sx={{ width: "100%", textAlign: "center" }}
            >
              No Recipients Found
            </Typography>
          ) : (
            <>
              <Typography variant="subtitle1">
                Who will receive a copy of this report?
              </Typography>
              <div style={{ height: 500, width: "100%", marginTop: "20px" }}>
                <DataGrid
                  rows={fields.map((field, index) => ({
                    ...field,
                    id: field.id,
                    rhfIndex: index,
                  }))}
                  columns={columns}
                  disableColumnMenu
                  disableRowSelectionOnClick
                  disableSelectionOnClick
                />
              </div>
            </>
          )}

          <div style={{ marginTop: 16 }}>
            {!isEdit && (
              <Button
                variant="outlined"
                onClick={() => setIsEdit(true)}
                sx={{ height: "45" }}
              >
                Edit
              </Button>
            )}
            {isEdit && (
              <>
                <Button
                  variant="contained"
                  onClick={handleAdd}
                  disabled={loading === "submitting"}
                  sx={{ height: "45" }}
                >
                  Add Row
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  style={{ marginLeft: 8 }}
                  onClick={handleSubmit(onSubmit)}
                  disabled={loading === "submitting"}
                  sx={{ height: "45" }}
                >
                  Save
                </Button>
                <Button
                  variant="outlined"
                  style={{ marginLeft: 8 }}
                  onClick={handleCancel}
                  disabled={loading === "submitting"}
                  sx={{ height: "45" }}
                >
                  Cancel
                </Button>
              </>
            )}
          </div>
        </form>
      )}
    </FormProvider>
  );
}
