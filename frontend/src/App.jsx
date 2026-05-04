import Sidebar from './components/Sidebar';
import ResumeUpload from './components/ResumeUpload';
import Dashboard from './components/Dashboard';

export default function App() {
    return (
        <div className="app-layout">
            <Sidebar />
            <main className="app-content">
                <ResumeUpload />
                <Dashboard />
            </main>
        </div>
    );
}
