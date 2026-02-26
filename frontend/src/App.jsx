import Navbar from './components/Navbar';
import ResumeUpload from './components/ResumeUpload';
import Dashboard from './components/Dashboard';

export default function App() {
    return (
        <>
            <Navbar />
            <div className="main-container">
                <ResumeUpload />
                <Dashboard />
            </div>
        </>
    );
}
