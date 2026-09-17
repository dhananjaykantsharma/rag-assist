import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { logout } from "../services/auth";
import { listDocuments, uploadDocument } from "../services/documents";

function Documents() {

  const navigate = useNavigate();

  const fileInputRef = useRef(null);

  const [file, setFile] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    listDocuments()
      .then((data) => {
        if (!cancelled) {
          setDocuments(data);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.response?.data?.detail || "Failed to load documents.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile) {
      setFile(selectedFile);
      setError("");
    }
  };

  const handleUpload = async () => {

    if (!file) {
      alert("Please select a document");
      return;
    }

    setUploading(true);
    setError("");

    try {
      const document = await uploadDocument(file);
      setDocuments((prev) => [document, ...prev]);
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="documents-page">

      <header className="dashboard-header">

        <div>
          <h1>My Documents</h1>

          <p>
            Upload documents and ask questions about them.
          </p>
        </div>

        <button onClick={handleLogout}>
          Logout
        </button>

      </header>

      <main className="documents-container">

        <div className="upload-box">

          <h2>Upload a Document</h2>

          <p>
            Upload PDF, TXT or DOCX files (max 10,000 words).
          </p>

          {error && <p className="auth-error">{error}</p>}

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.docx"
            onChange={handleFileChange}
          />

          {file && (
            <div className="selected-file">
              <strong>{file.name}</strong>

              <span>
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </span>
            </div>
          )}

          <button onClick={handleUpload} disabled={uploading}>
            {uploading ? "Uploading..." : "Upload Document"}
          </button>

        </div>

        <div className="document-list">

          <h2>Your Documents</h2>

          {loading && <p>Loading documents...</p>}

          {!loading && documents.length === 0 && (
            <p>No documents uploaded yet.</p>
          )}

          {documents.map((document) => (

            <div className="document-card" key={document.id}>

              <div>
                <h3>{document.filename}</h3>

                <p>
                  {document.word_count} words · {document.chunk_count} chunks
                </p>
              </div>

              <Link to={`/chat/${document.id}`}>
                Ask Questions →
              </Link>

            </div>

          ))}

        </div>

      </main>

    </div>
  );
}

export default Documents;
