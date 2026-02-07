<template>
  <v-container>
    <!-- Top bar -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div class="d-flex align-center">
        <v-icon color="primary" class="mr-2">mdi-clipboard-text-outline</v-icon>
        <h2 class="text-h5 font-weight-bold">ISMS Dashboard</h2>
      </div>

      <div>
        <v-btn
          color="primary"
          class="mr-2"
          @click="$router.push('/dashboard')"
        >
          Home
        </v-btn>
        <v-btn
          color="info"
          class="mr-2"
          @click="$router.push({ path: '/generated_files', query: { category: 'ISMS' } })"
        >
          My Generated Files
        </v-btn>
        <v-btn color="error" @click="logoutUser">Logout</v-btn>
      </div>
    </div>

    <v-alert type="info" dense border="left" class="mb-4">
      📌 You are working in the <strong>ISMS Category</strong>.  
      Upload ISMS-specific Excel files and generate Word documents with ISMS templates.
    </v-alert>

    <v-card class="pa-6 mb-6" outlined>
      <h3 class="mb-4">Upload ISMS File</h3>

      <v-file-input
        v-model="selectedFile"
        label="Select Excel/CSV file"
        accept=".xlsx,.xls,.csv,.xlsm"
        outlined
        dense
        class="mb-4"
      ></v-file-input>

      <v-btn
        color="primary"
        class="mb-4"
        :disabled="!selectedFile"
        @click="uploadFile"
      >
        Upload File
      </v-btn>

      <!-- Data table -->
      <v-data-table
        :headers="headers"
        :items="excelRows"
        item-key="id"
        dense
        class="elevation-1"
      >
        <template v-slot:item.actions="{ item }">
          <v-btn
            small
            color="success"
            :disabled="item.Status === 'Generated'"
            @click="autoGenerateWord(item)"
          >
            Generate
          </v-btn>
          <v-btn
            small
            color="red"
            v-if="item.Status === 'Generated'"
            @click="deleteGeneratedDoc(item)"
          >
            Delete
          </v-btn>
        </template>

        <template v-slot:item.checklist="{ item }">
          <v-btn
            small
            color="secondary"
            :disabled="item.ChecklistGenerated"
            @click="generateChecklist(item.id)"
          >
            Checklist
          </v-btn>
          <v-btn
            small
            color="red"
            @click="deleteChecklist(item)"
            v-if="item.ChecklistGenerated"
          >
            Delete Checklist
          </v-btn>
        </template>

        <template v-slot:item.Status="{ item }">
          <span
            :class="{
              'text-success font-weight-bold': item.Status === 'Generated',
              'text-info': item.Status === 'Pending'
            }"
          >
            {{ item.Status }}
          </span>
        </template>
      </v-data-table>
    </v-card>

    <!-- Status messages -->
    <v-alert
      v-if="message"
      type="info"
      class="mt-4"
      dense
      border="left"
    >
      {{ message }}
    </v-alert>

    <v-overlay
      v-model="loading"
      class="d-flex align-center justify-center"
      scrim="#000"
      opacity="0.7"
    >
      <div class="text-center">
        <v-progress-circular
          indeterminate
          size="64"
          color="primary"
        />
        <p class="mt-4 text-white text-lg">Generating document... Please wait</p>
      </div>
    </v-overlay>
  </v-container>
</template>


<script>
import axios from "axios";

export default {
  data: () => ({
    selectedCompany: localStorage.getItem("company") || "APL",
    message: "",
    excelRows: [],
    templateDialog: false,
    selectedRowId: null,
    selectedFile: null,
    selectedFileId: null,
    userFiles: [],
    currentUserGeneratedRowIds: [],
    headers: [
      { title: "ID", value: "id" },
      { title: "Organization Name", value: "Organization_Name" },
      { title: "Address", value: "Address" },
      { title: "Scope/s", value: "Scope_s" },
      { title: 'Mandays', value: 'MANDAY'},
      { title: "Status", value: "Status" },
      { title: "Checklist", value: "checklist", sortable: false },
      { title: "Actions", value: "actions", sortable: false }
    ],
    loading: false
  }),
  mounted() {
    this.fetchUserFiles();
    this.fetchCurrentUserGeneratedRows();
  },
  methods: {
    logoutUser() {
      localStorage.removeItem("token");
      this.$router.push("/login");
    },

    async uploadFile() {
      if (!this.selectedFile) return;
      this.message = "";

      try {
        const token = localStorage.getItem("token");
        const company = localStorage.getItem("company") || "APL";
        const formData = new FormData();
        formData.append("file", this.selectedFile);
        formData.append("category", "ISMS");
        formData.append("company", company);

        const res = await axios.post(
          "https://kvqa-data-application.onrender.com/upload-file",
          // "https://kvqa-data-application.onrender.com/upload-file",
          formData,
          {
            headers: { Authorization: `Bearer ${token}`, "Content-Type": "multipart/form-data" }
          }
        );

        this.message = res.data.message;
        this.selectedFile = null;

        this.selectedFileId = res.data.file_id;

        await this.fetchUserFiles();
        await this.fetchExcelRows();
        await this.fetchCurrentUserGeneratedRows();
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = err.response?.data?.error || "File upload failed!";
      }
    },

    async fetchUserFiles() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("https://kvqa-data-application.onrender.com/my-files", {
        // const res = await axios.get("http://127.0.0.1:5000/my-files", {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.userFiles = res.data;
      } catch (err) {
        console.error(err.response?.data || err);
      }
    },

    async fetchCurrentUserGeneratedRows() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("https://kvqa-data-application.onrender.com/generated-docs", {
        // const res = await axios.get("http://127.0.0.1:5000/generated-docs", {
          headers: { Authorization: `Bearer ${token}` }
        });
        // Store row_ids of current user for freeze logic
        this.currentUserGeneratedRowIds = res.data.map(d => d.row_id);
      } catch (err) {
        console.error(err.response?.data || err);
      }
    },

    async fetchExcelRows() {
      if (!this.selectedFileId) return;
      this.message = "";

      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(
          `https://kvqa-data-application.onrender.com/excel-rows/${this.selectedFileId}`,
          // `http://127.0.0.1:5000/excel-rows/${this.selectedFileId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        if (Array.isArray(res.data)) {
          this.excelRows = res.data.map(row => ({
            ...row,
            generatedByCurrentUser: this.currentUserGeneratedRowIds.includes(row.id)
          }));
        } else {
          this.excelRows = [];
          this.message = res.data?.error || "Failed to fetch data!";
        }
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = err.response?.data?.error || "Failed to fetch data!";
      }
    },

    // autoGenerateWord(row) {
    //   const manday = String(row.MANDAY).trim();

    //   let templateType = null;
    //   if (manday === "7" || manday === "7_manday") {
    //     templateType = "7_manday";
    //   // } else if (manday === "8" || manday === "8_manday") {
    //   //   templateType = "8_manday";
    //   // } else if (manday === "9" || manday === "9_manday") {
    //   //   templateType = "9_manday";
    //   } else {
    //     this.message = `⚠️ Cannot generate document: unsupported MANDAY value "${row.MANDAY}"`;
    //     return;
    //   }

    //   this.generateWord(row.id, templateType);
    // },

    // autoGenerateWord(row) {
    //   // ISMS is manday-independent
    //   this.generateWord(row.id);
    // },

    // async generateWord(rowId, templateType) {
    //   this.templateDialog = false;
    //   this.message = "";
    //   this.loading = true;

    //   try {
    //     const token = localStorage.getItem("token");
    //     const company = localStorage.getItem("company") || "APL";
    //     // const res = await axios.get(
    //     //   `http://127.0.0.1:5000/generate-docx-isms/${this.selectedFileId}/${rowId}?template_type=${templateType}`,
    //     //   // `http://127.0.0.1:5000/generate-docx/${this.selectedFileId}/${rowId}?template_type=${templateType}`,
    //     //   { 
    //     //     headers: { Authorization: `Bearer ${token}` }, 
    //     //     responseType: "blob", 
    //     //     params: {
    //     //       template_type: templateType,
    //     //       company: company
    //     //     } 
    //     //   }
    //     // );

    //     const res = await axios.get(
    //       `http://127.0.0.1:5000/generate-docx-isms/${this.selectedFileId}`,
    //       {
    //         headers: { Authorization: `Bearer ${token}` },
    //         responseType: "blob",
    //         params: {
    //           company: company
    //         }
    //       }
    //     );

    //     // Get org name from the row data
    //     const row = this.excelRows.find(r => r.id === rowId);
    //     const orgName = row?.Organization_Name || `record_${rowId}`;
    //     // const safeName = orgName.replace(/[^a-z0-9_\- ]/gi, "_");
    //     const safeName = orgName.replace(/[^a-z0-9_\- ]/gi, "_").trim();

    //     const url = window.URL.createObjectURL(new Blob([res.data]));
    //     const link = document.createElement("a");
    //     link.href = url;
    //     // link.setAttribute("download", `${safeName}_${templateType}.docx`);
    //     link.setAttribute("download", `${safeName}.docx`);
    //     document.body.appendChild(link);
    //     link.click();

    //     this.message = `Word document generated for ${orgName} with ${templateType}`;
    //     await this.fetchCurrentUserGeneratedRows();
    //     await this.fetchExcelRows();
    //   } catch (err) {
    //     console.error(err.response?.data || err);
    //     this.message = "Failed to generate Word document!";
    //   } finally {
    //     this.loading = false;
    //   }
    // },

//   async generateWord(rowId) {
//   this.message = "";
//   this.loading = true;

//   try {
//     const token = localStorage.getItem("token");
//     const company = localStorage.getItem("company") || "CSPL";

//     // Get org name from the table
//     const row = this.excelRows.find(r => r.id === rowId);
//     const orgName = row?.["Organization_Name"] || "ISMS_Record";
//     const safeName = orgName.replace(/[^a-z0-9_\- ]/gi, "_").trim();

//     // Pass org name to backend
//     const res = await axios.get(
//       `http://127.0.0.1:5000/generate-docx-isms/${this.selectedFileId}`,
//       {
//         headers: { Authorization: `Bearer ${token}` },
//         responseType: "blob",
//         params: { company, org_name: orgName } // <-- pass org_name
//       }
//     );

//     // Download file
//     const url = window.URL.createObjectURL(new Blob([res.data]));
//     const link = document.createElement("a");
//     link.href = url;
//     link.setAttribute("download", `${safeName}.docx`);
//     document.body.appendChild(link);
//     link.click();

//     this.message = `✅ ISMS document generated for ${orgName}`;
//     await this.fetchCurrentUserGeneratedRows();
//     await this.fetchExcelRows();

//   } catch (err) {
//     console.error(err);
//     this.message = "Failed to generate ISMS document!";
//   } finally {
//     this.loading = false;
//   }
// },

  autoGenerateWord(row) {
    // Compute exact Excel column index: Column A=0 (field names), Column B=1 (first company)
    const colId = this.excelRows.findIndex(r => r.id === row.id) + 1;
    this.generateWord(row, colId);
  },

  async generateWord(row, colId) {
    this.message = "";
    this.loading = true;

    try {
      const token = localStorage.getItem("token");
      const company = localStorage.getItem("company") || "CSPL";

      const orgName = row?.Organization_Name || "ISMS_Record";
      const safeName = orgName.replace(/[^a-z0-9_\- ]/gi, "_").trim();

      // Call backend with exact col_id
      const res = await axios.get(
        `https://kvqa-data-application.onrender.com/generate-docx-isms/${this.selectedFileId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: "blob",
          params: { company, org_name: orgName, col_id: colId }
        }
      );

      // Download DOCX
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${safeName}.docx`);
      document.body.appendChild(link);
      link.click();

      this.message = `✅ ISMS document generated for ${orgName}`;
      await this.fetchCurrentUserGeneratedRows();
      await this.fetchExcelRows();

    } catch (err) {
      console.error(err);
      this.message = "Failed to generate ISMS document!";
    } finally {
      this.loading = false;
    }
  },

    async generateChecklist(rowId) {
      this.message = "";
      this.loading = true;

      try {
        const token = localStorage.getItem("token");
        const company = localStorage.getItem("company") || "APL";
        const res = await axios.get(
          `https://kvqa-data-application.onrender.com/generate-checklist/${this.selectedFileId}/${rowId}`,
          {
            headers: { Authorization: `Bearer ${token}` },
            responseType: "blob",
            params: {
              company: company
            }
          }
        );

        // Find org name for file naming
        const row = this.excelRows.find(r => r.id === rowId);
        // const orgName = row?.Organization_Name || `record_${rowId}`;
        const orgName = row?.["Organization Name"] || "ISMS_Record";
        console.log(orgName);
        const safeName = orgName.replace(/[^a-z0-9_\- ]/gi, "_").trim();

        // Download file
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `${safeName}_ISMS_checklist.docx`);
        document.body.appendChild(link);
        link.click();

        this.message = `Checklist generated for ${orgName}`;
        row.ChecklistGenerated = true;
      } catch (err) {
        console.error("Axios error:", err);

        if (err.response && err.response.data instanceof Blob) {
          try {

            const text = await err.response.data.text();
            const errorJson = JSON.parse(text);
            this.message = errorJson.error || "Failed to generate Checklist!";
          } catch (e) {
            this.message = "Failed to generate Checklist!";
          }
          alert(this.message);
        } else if (err.response) {
          this.message = err.response.data?.error || "Failed to generate Checklist!";
          alert(this.message);
        } else {
          this.message = err.message || "Failed to generate Checklist!";
          alert(this.message);
        }
      } finally {
        this.loading = false;
      }
    },

    async deleteGeneratedDoc(row) {
      if (!confirm(`Are you sure you want to delete the generated doc for ${row.Organization_Name}?`)) return;

      this.loading = true;
      this.message = "";

      try {
        const token = localStorage.getItem("token");
        const category = row.Category || "ISMS"; // pass current category
        await axios.delete(
          `https://kvqa-data-application.onrender.com/delete-generated/${category}/${row.id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        this.message = `Deleted generated document for ${row.Organization_Name}`;
        row.Status = "Pending";
        await this.fetchCurrentUserGeneratedRows();
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = err.response?.data?.error || "Failed to delete document!";
      } finally {
        this.loading = false;
      }
    },

    async deleteChecklist(row) {
      if (!confirm(`Are you sure you want to delete the checklist for ${row.Organization_Name}?`)) return;

      this.loading = true;
      this.message = "";

      try {
        const token = localStorage.getItem("token");
        const category = row.Category || "ISMS";
        await axios.delete(
          `https://kvqa-data-application.onrender.com/delete-checklist/${category}/${row.id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        this.message = `Deleted checklist for ${row.Organization_Name}`;
        row.ChecklistGenerated = false;

      } catch (err) {
        console.error(err.response?.data || err);
        this.message = err.response?.data?.error || "Failed to delete checklist!";
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>