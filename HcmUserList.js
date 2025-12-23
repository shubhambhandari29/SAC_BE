import { useState, useEffect, useRef } from "react";
import {
  useForm,
  FormProvider,
  useFieldArray,
  Controller,
} from "react-hook-form";
import {
  Button,
  MenuItem,
  Select,
  TextField,
  Typography,
  useTheme,
} from "@mui/material";
// import { MdOutlineCancel } from "react-icons/md";
import api from "../../../../../api/api";
import Loader from "../../../../ui/Loader";
import { DataGrid } from "@mui/x-data-grid";
import Swal from "sweetalert2";
import { formatPhoneNumber } from "../../../../../util";

export default function HCMUserList({ customerNum }) {
  const [isEdit, setIsEdit] = useState(false);
  const [originalData, setOriginalData] = useState([]);
  const methods = useForm({
    defaultValues: {
      users: [],
    },
  });
  const [loading, setLoading] = useState("");
  const { control, handleSubmit, reset } = methods;
  const { fields, append, remove } = useFieldArray({
    control,
    name: "users",
  });
  const gridRef = useRef();
  const theme = useTheme();

  useEffect(() => {
    const fetchData = async () => {
      setLoading("fetching");
      try {
        const res = await api.get("/hcm_users/", {
          params: { CustomerNum: customerNum },
        });

        setOriginalData(res.data);
        reset({ users: res.data });
      } catch (err) {
        console.error("Failed to fetch users:", err);
      } finally {
        setLoading("");
      }
    };
    fetchData();
  }, [customerNum, reset]);

  const onSubmit = (data) => {
    const isSame = JSON.stringify(data.users) === JSON.stringify(originalData);

    if (isSame) {
      reset({ users: data.users });
      setIsEdit(false);
      return;
    }

    try {
      setLoading("submitting");
      api.post(`/hcm_users/upsert`, data.users);
    } catch (err) {
      console.log(err);
    } finally {
      setLoading("");
    }

    setOriginalData(data.users);
    reset({ users: data.users });
    setIsEdit(false);
  };

  const handleAdd = () => {
    append({
      CustomerNum: customerNum,
      UserName: "",
      UserTitle: "",
      UserEmail: "",
      TelNum: "",
      UserAction: "",
      LanID: "",
      UserID: "",
      PROD_Password: "",
      UAT_Password: "rsa123",
    });

    setTimeout(() => {
      const api = gridRef.current;
      if (!api) return;

      api.scrollToIndexes({ rowIndex: fields.length });
    }, 0);
  };

  const handleCancel = () => {
    setIsEdit(false);
    if (fields.length > originalData.length) remove(fields.length - 1);
  };

  const columns = [
    {
      field: "UserName",
      headerName: (
        <b>
          User Name<sup style={{ color: "red" }}>*</sup>
        </b>
      ),
      flex: 1,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`users.${params.row.rhfIndex}.UserName`}
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                sx={{ m: "5px 0px" }}
                onKeyDown={(event) => event.stopPropagation()}
                required
              />
            )}
          />
        ) : (
          params.value
        ),
    },
    {
      field: "UserTitle",
      headerName: (
        <b>
          Title<sup style={{ color: "red" }}>*</sup>
        </b>
      ),
      flex: 1,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`users.${params.row.rhfIndex}.UserTitle`}
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                sx={{ m: "5px 0px" }}
                onKeyDown={(event) => event.stopPropagation()}
                required
              />
            )}
          />
        ) : (
          params.value
        ),
    },
    {
      field: "UserEmail",
      headerName: (
        <b>
          E-Mail<sup style={{ color: "red" }}>*</sup>
        </b>
      ),
      flex: 1,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`users.${params.row.rhfIndex}.UserEmail`}
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                sx={{ m: "5px 0px" }}
                onKeyDown={(event) => event.stopPropagation()}
                required
              />
            )}
          />
        ) : (
          params.value
        ),
    },
    {
      field: "TelNum",
      headerName: <b>Telephone Number</b>,
      flex: 1,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`users.${params.row.rhfIndex}.TelNum`}
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                sx={{ m: "5px 0px" }}
                onKeyDown={(event) => event.stopPropagation()}
                onChange={(e) => {
                  const formattedValue = formatPhoneNumber(e.target.value);
                  field.onChange(formattedValue);
                }}
              />
            )}
          />
        ) : (
          params.value
        ),
    },
    {
      field: "UserAction",
      headerName: (
        <b>
          User Action<sup style={{ color: "red" }}>*</sup>
        </b>
      ),
      flex: 1,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`users.${params.row.rhfIndex}.UserAction`}
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                label="SAC 1"
                sx={{ m: "5px 0px", height: "40px", minWidth: "130px" }}
                onKeyDown={(event) => event.stopPropagation()}
              >
                <MenuItem value="Add">Add</MenuItem>
                <MenuItem value="Delete">Delete</MenuItem>
                <MenuItem value="No Change">No Change</MenuItem>
                <MenuItem value="No Change">Modify</MenuItem>
              </Select>
            )}
          />
        ) : (
          params.value
        ),
    },
    {
      field: "LanID",
      headerName: (
        <b>
          LAN ID<sup style={{ color: "red" }}>*</sup>
        </b>
      ),
      flex: 1,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`users.${params.row.rhfIndex}.LanID`}
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                sx={{ m: "5px 0px" }}
                onKeyDown={(event) => event.stopPropagation()}
                required
              />
            )}
          />
        ) : (
          params.value
        ),
    },
    {
      field: "UserID",
      headerName: <b>User ID</b>,
      flex: 1,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`users.${params.row.rhfIndex}.UserID`}
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
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
      field: "PROD_Password",
      headerName: <b>Production Password</b>,
      flex: 1,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`users.${params.row.rhfIndex}.PROD_Password`}
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
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
      field: "UAT_Password",
      headerName: <b>UAT Password</b>,
      flex: 1,
      renderCell: (params) =>
        isEdit ? (
          <Controller
            name={`users.${params.row.rhfIndex}.UAT_Password`}
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                sx={{ m: "5px 0px" }}
                onKeyDown={(event) => event.stopPropagation()}
              />
            )}
          />
        ) : (
          params.value
        ),
    },
  ];

  if (loading) return <Loader size={40} height="540px" />;

  return (
    <FormProvider {...methods}>
      <form>
        {fields.length === 0 ? (
          <Typography
            variant="h6"
            sx={{ width: "100%", display: "grid", placeItems: "center" }}
          >
            No Affiliates Found
          </Typography>
        ) : (
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
              initialState={{
                pagination: { paginationModel: { page: 0, pageSize: 25 } },
              }}
              pageSizeOptions={[25, 50]}
              apiRef={gridRef}
            />
          </div>
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
    </FormProvider>
  );
}
