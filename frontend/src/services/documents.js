import api from "./api";

export async function listDocuments() {
  const response = await api.get("/api/documents");
  return response.data;
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/api/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
}

export async function askDocument(documentId, question) {
  const response = await api.post(`/api/documents/${documentId}/ask`, { question });
  return response.data;
}
