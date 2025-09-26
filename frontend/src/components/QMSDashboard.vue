<!-- <template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
      <h2>Sales Dashboard</h2>
      <v-btn
        color="info"
        class="mb-4"
        @click="$router.push('/generated_files')"
      >
        My Generated Files
      </v-btn>

      <v-btn color="error" @click="logoutUser">Logout</v-btn>
      
    </div> -->

    <!-- Section to upload Excel/CSV file -->
    <!-- <v-card class="pa-6 mb-6" outlined>
      <h3 class="mb-4">Upload Your File</h3>

      <v-file-input
        v-model="selectedFile"
        label="Select Excel/CSV file"
        accept=".xlsx,.xls,.csv"
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
      </v-btn> -->

      <!-- Previously uploaded files -->
      <!-- <h3 class="mb-2">Your Uploaded Files</h3>
      <v-select
        v-model="selectedFileId"
        :items="userFiles"
        item-text="file_name"
        item-value="id"
        label="Select a file to view data"
        outlined
        dense
        class="mb-4"
        @change="fetchExcelRows"
      ></v-select> -->

      <!-- Table to display Excel rows -->
      <!-- <v-data-table
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
            :disabled="item.generatedByCurrentUser"
            @click="openTemplateDialog(item.id)"
          >
            Generate Word
          </v-btn>
        </template>
      </v-data-table> -->
      <!-- <v-data-table
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
      @click="openTemplateDialog(item.id)"
    >
      Generate Word
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

    </v-card> -->

    <!-- Template Selection Dialog -->
    <!-- <v-dialog v-model="templateDialog" max-width="400">
      <v-card>
        <v-card-title>Select Template</v-card-title>
        <v-card-text>
          <v-btn
            block
            color="primary"
            class="mb-2"
            @click="generateWord(selectedRowId, 'template2')"
          >
            6 Manday
          </v-btn>
          <v-btn
            block
            color="secondary"
            @click="generateWord(selectedRowId, 'template1')"
          >
            3 Manday
          </v-btn>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="templateDialog = false">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog> -->

    <!-- Status messages -->
    <!-- <v-alert
      v-if="message"
      type="info"
      class="mt-4"
      dense
      border="left"
    >
      {{ message }}
    </v-alert>
  </v-container>
</template> -->

<!-- <template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
      <div class="d-flex align-center">
        <v-icon color="primary" class="mr-2">mdi-clipboard-text-outline</v-icon>
        <h2 class="text-h5 font-weight-bold">QMS Dashboard</h2>
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
          @click="$router.push('/generated_files')"
        >
          My Generated Files
        </v-btn>
        <v-btn color="error" @click="logoutUser">Logout</v-btn>
      </div>
    </div>

    <v-alert type="info" dense border="left" class="mb-4">
      📌 You are working in the <strong>QMS Category</strong>.  
      Upload QMS-specific Excel files and generate Word documents with QMS templates.
    </v-alert>

    <v-card class="pa-6 mb-6" outlined>
      <h3 class="mb-4">Upload QMS File</h3>

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

      <h3 class="mb-2">Your QMS Uploaded Files</h3>
      <v-select
        v-model="selectedFileId"
        :items="userFiles"
        item-text="file_name"
        item-value="id"
        label="Select a QMS file to view data"
        outlined
        dense
        class="mb-4"
        @change="fetchExcelRows"
      />

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
      // { title: 'Custom Date', value: 'certification_audit_conducted'},
      // { title: 'Issue No', value: 'INTERNAL_ISSUE_NO'},
      { title: "Status", value: "Status" },
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

    // Upload file and immediately load its content
    async uploadFile() {
      if (!this.selectedFile) return;
      this.message = "";

      try {
        const token = localStorage.getItem("token");
        const formData = new FormData();
        formData.append("file", this.selectedFile);
        formData.append("category", "QMS");

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
        // const res = await axios.get("https://kvqa-data-application.onrender.com/my-files", {
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
        // const res = await axios.get("https://kvqa-data-application.onrender.com/generated-docs", {
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
          // `https://kvqa-data-application.onrender.com/excel-rows/${this.selectedFileId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        if (Array.isArray(res.data)) {
          // Mark only rows generated by current user
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

    // openTemplateDialog(rowId) {
    //   this.selectedRowId = rowId;
    //   this.templateDialog = true;
    // },

    autoGenerateWord(row) {
      const manday = String(row.MANDAY).trim();

      let templateType = null;
      if (manday === "6" || manday === "6_manday") {
        templateType = "6_manday";
      } else if (manday === "3" || manday === "3_manday") {
        templateType = "3_manday";
      } else {
        this.message = `⚠️ Cannot generate document: unsupported MANDAY value "${row.MANDAY}"`;
        return;
      }

      this.generateWord(row.id, templateType);
    },

    async generateWord(rowId, templateType) {
      this.templateDialog = false;
      this.message = "";
      this.loading = true;

      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(
          `https://kvqa-data-application.onrender.com/generate-docx/${this.selectedFileId}/${rowId}?template_type=${templateType}`,
          // `https://kvqa-data-application.onrender.com/generate-docx/${this.selectedFileId}/${rowId}?template_type=${templateType}`,
          { headers: { Authorization: `Bearer ${token}` }, responseType: "blob" }
        );

        // Get org name from the row data
        const row = this.excelRows.find(r => r.id === rowId);
        const orgName = row?.Organization_Name || `record_${rowId}`;
        // const safeName = orgName.replace(/[^a-z0-9_\- ]/gi, "_");
        const safeName = orgName.replace(/[^a-z0-9_\- ]/gi, "_").trim();

        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        // link.setAttribute("download", `${safeName}_${templateType}.docx`);
        link.setAttribute("download", `${safeName}.docx`);
        document.body.appendChild(link);
        link.click();

        this.message = `Word document generated for ${orgName} with ${templateType}`;
        await this.fetchCurrentUserGeneratedRows();
        await this.fetchExcelRows();
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = "Failed to generate Word document!";
      } finally {
        this.loading = false;
      }
    }
  }
};
</script> -->

<template>
  <v-container>
    <!-- Top bar -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div class="d-flex align-center">
        <v-icon color="primary" class="mr-2">mdi-clipboard-text-outline</v-icon>
        <h2 class="text-h5 font-weight-bold">QMS Dashboard</h2>
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
          @click="$router.push('/generated_files')"
        >
          My Generated Files
        </v-btn>
        <v-btn color="error" @click="logoutUser">Logout</v-btn>
      </div>
    </div>

    <!-- Info Banner -->
    <v-alert type="info" dense border="left" class="mb-4">
      📌 You are working in the <strong>QMS Category</strong>.  
      Upload QMS-specific Excel files and generate Word documents with QMS templates.
    </v-alert>

    <!-- Section to upload Excel/CSV file -->
    <v-card class="pa-6 mb-6" outlined>
      <h3 class="mb-4">Upload QMS File</h3>

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

      <!-- Uploaded files -->
      <!-- <h3 class="mb-2">Your QMS Uploaded Files</h3>
      <v-select
        v-model="selectedFileId"
        :items="userFiles"
        item-text="file_name"
        item-value="id"
        label="Select a QMS file to view data"
        outlined
        dense
        class="mb-4"
        @change="fetchExcelRows"
      /> -->

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
            :disabled="!item.ChecklistAvailable || item.ChecklistGenerated"
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

    <!-- Template Selection Dialog -->
    <!-- <v-dialog v-model="templateDialog" max-width="400">
      <v-card>
        <v-card-title>Select Template</v-card-title>
        <v-card-text>
          <v-btn
            block
            color="primary"
            class="mb-2"
            @click="generateWord(selectedRowId, '6_manday')"
          >
            6 Manday
          </v-btn>
          <v-btn
            block
            color="secondary"
            @click="generateWord(selectedRowId, '3_manday')"
          >
            3 Manday
          </v-btn>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="templateDialog = false">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog> -->

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
      // { title: 'Custom Date', value: 'certification_audit_conducted'},
      // { title: 'Issue No', value: 'INTERNAL_ISSUE_NO'},
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

    // Upload file and immediately load its content
    async uploadFile() {
      if (!this.selectedFile) return;
      this.message = "";

      try {
        const token = localStorage.getItem("token");
        const formData = new FormData();
        formData.append("file", this.selectedFile);
        formData.append("category", "QMS");

        const res = await axios.post(
          "http://127.0.0.1:5000/upload-file",
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
        const res = await axios.get("http://127.0.0.1:5000/my-files", {
        // const res = await axios.get("https://kvqa-data-application.onrender.com/my-files", {
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
        const res = await axios.get("http://127.0.0.1:5000/generated-docs", {
        // const res = await axios.get("https://kvqa-data-application.onrender.com/generated-docs", {
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
          `http://127.0.0.1:5000/excel-rows/${this.selectedFileId}`,
          // `https://kvqa-data-application.onrender.com/excel-rows/${this.selectedFileId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        if (Array.isArray(res.data)) {
          // Mark only rows generated by current user
          this.excelRows = res.data.map(row => ({
            ...row,
            generatedByCurrentUser: this.currentUserGeneratedRowIds.includes(row.id),
            ChecklistGenerated: row.ChecklistGenerated || false
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

    // openTemplateDialog(rowId) {
    //   this.selectedRowId = rowId;
    //   this.templateDialog = true;
    // },

    autoGenerateWord(row) {
      const manday = String(row.MANDAY).trim();

      let templateType = null;
      if (manday === "6" || manday === "6_manday") {
        templateType = "6_manday";
      } else if (manday === "3" || manday === "3_manday") {
        templateType = "3_manday";
      } else {
        this.message = `⚠️ Cannot generate document: unsupported MANDAY value "${row.MANDAY}"`;
        return;
      }

      this.generateWord(row.id, templateType);
    },

    async generateWord(rowId, templateType) {
      this.templateDialog = false;
      this.message = "";
      this.loading = true;

      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(
          `http://127.0.0.1:5000/generate-docx/${this.selectedFileId}/${rowId}?template_type=${templateType}`,
          // `https://kvqa-data-application.onrender.com/generate-docx/${this.selectedFileId}/${rowId}?template_type=${templateType}`,
          { headers: { Authorization: `Bearer ${token}` }, responseType: "blob" }
        );

        // Get org name from the row data
        const row = this.excelRows.find(r => r.id === rowId);
        const orgName = row?.Organization_Name || `record_${rowId}`;
        // const safeName = orgName.replace(/[^a-z0-9_\- ]/gi, "_");
        const safeName = orgName.replace(/[^a-z0-9_\- ]/gi, "_").trim();

        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        // link.setAttribute("download", `${safeName}_${templateType}.docx`);
        link.setAttribute("download", `${safeName}.docx`);
        document.body.appendChild(link);
        link.click();

        this.message = `Word document generated for ${orgName} with ${templateType}`;
        await this.fetchCurrentUserGeneratedRows();
        await this.fetchExcelRows();
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = "Failed to generate Word document!";
      } finally {
        this.loading = false;
      }
    },

    // async generateChecklist(rowId) {
    //   this.message = "";
    //   this.loading = true;

    //   try {
    //     const token = localStorage.getItem("token");
    //     const res = await axios.get(
    //       `http://127.0.0.1:5000/generate-checklist/${this.selectedFileId}/${rowId}`,
    //       {
    //         headers: { Authorization: `Bearer ${token}` },
    //         responseType: "blob"
    //       }
    //     );

    //     // Find org name for file naming
    //     const row = this.excelRows.find(r => r.id === rowId);
    //     const orgName = row?.Organization_Name || `record_${rowId}`;
    //     const safeName = orgName.replace(/[^a-z0-9_\- ]/gi, "_").trim();

    //     // Download file
    //     const url = window.URL.createObjectURL(new Blob([res.data]));
    //     const link = document.createElement("a");
    //     link.href = url;
    //     link.setAttribute("download", `${safeName}_QMS_checklist.docx`);
    //     document.body.appendChild(link);
    //     link.click();

    //     this.message = `Checklist generated for ${orgName}`;
    //     row.ChecklistGenerated = true;
    //   } catch (err) {
    //     console.error(err.response?.data || err);
    //     this.message = "Failed to generate Checklist!";
    //   } finally {
    //     this.loading = false;
    //   }
    // },

    async generateChecklist(rowId) {
      this.message = "";
      this.loading = true;

      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(
          `http://127.0.0.1:5000/generate-checklist/${this.selectedFileId}/${rowId}`,
          {
            headers: { Authorization: `Bearer ${token}` },
            responseType: "blob"
          }
        );

        // Find org name for file naming
        const row = this.excelRows.find(r => r.id === rowId);
        const orgName = row?.Organization_Name || `record_${rowId}`;
        console.log(orgName);
        const safeName = orgName.replace(/[^a-z0-9_\- ]/gi, "_").trim();

        // Download file
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `${safeName}_QMS_checklist.docx`);
        document.body.appendChild(link);
        link.click();

        this.message = `Checklist generated for ${orgName}`;
        row.ChecklistGenerated = true;
      // } catch (err) {
      //   console.error(err.response?.data || err);
      //   this.message = err.response?.data?.error || "Failed to generate Checklist!";
      //   alert(this.message);
      } catch (err) {
        console.error("Axios error:", err);

        if (err.response && err.response.data instanceof Blob) {
          try {
            // Convert blob -> text -> JSON
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
        const category = row.Category || "QMS"; // pass current category
        await axios.delete(
          `http://127.0.0.1:5000/delete-generated/${category}/${row.id}`,
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
        const category = row.Category || "QMS"; // pass current category
        await axios.delete(
          `http://127.0.0.1:5000/delete-checklist/${category}/${row.id}`,
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