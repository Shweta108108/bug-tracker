import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import { ToastProvider } from "./components/ui/ToastProvider";
import IssueDetailPage from "./pages/IssueDetailPage";
import LoginPage from "./pages/LoginPage";
import NotFoundPage from "./pages/NotFoundPage";
import ProjectIssuesPage from "./pages/ProjectIssuesPage";
import ProjectsListPage from "./pages/ProjectsListPage";
import SignupPage from "./pages/SignupPage";

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route element={<ProtectedRoute />}>
              <Route path="/projects" element={<ProjectsListPage />} />
              <Route path="/projects/:projectId/issues" element={<ProjectIssuesPage />} />
              <Route path="/projects/:projectId/issues/:issueId" element={<IssueDetailPage />} />
            </Route>
            <Route path="/" element={<Navigate to="/projects" replace />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ToastProvider>
  );
}

export default App;
