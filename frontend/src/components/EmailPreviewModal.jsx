import { useState } from 'react';
import { sendEmail } from '../api/api';

export default function EmailPreviewModal({ preview, onClose, onSent }) {
    const [to, setTo] = useState(preview.to || '');
    const [subject, setSubject] = useState(preview.subject || '');
    const [body, setBody] = useState(preview.body || '');
    const [sending, setSending] = useState(false);
    const [result, setResult] = useState(null);

    const handleSend = async () => {
        if (!to.trim()) {
            setResult({ type: 'error', message: 'Please enter a recipient email address.' });
            return;
        }
        setSending(true);
        setResult(null);
        try {
            const data = await sendEmail({
                job_id: preview.job_id,
                to: to.trim(),
                subject,
                body,
            });
            if (data.status === 'sent') {
                setResult({ type: 'success', message: `Email sent to ${data.to} for ${data.role} at ${data.company}!` });
                setTimeout(() => {
                    onSent?.();
                    onClose();
                }, 1500);
            } else {
                setResult({ type: 'error', message: data.message || 'Failed to send email.' });
            }
        } catch (err) {
            setResult({ type: 'error', message: 'Failed to send email. Check backend.' });
        } finally {
            setSending(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2 className="modal-title">
                        <span className="modal-icon">✉️</span>
                        Compose Email
                    </h2>
                    <button className="modal-close" onClick={onClose}>✕</button>
                </div>

                <div className="modal-subheader">
                    <span className="modal-job-info">
                        {preview.role} at <strong>{preview.company}</strong>
                    </span>
                    {preview.has_resume && (
                        <span className="modal-resume-badge">📎 Resume attached</span>
                    )}
                </div>

                <div className="modal-body">
                    <div className="form-group">
                        <label className="form-label">To</label>
                        <input
                            id="email-to"
                            type="email"
                            className="form-input"
                            value={to}
                            onChange={(e) => setTo(e.target.value)}
                            placeholder="recruiter@company.com"
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group form-group-half">
                            <label className="form-label">From</label>
                            <input
                                type="text"
                                className="form-input form-input-readonly"
                                value={preview.from || ''}
                                readOnly
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Subject</label>
                        <input
                            id="email-subject"
                            type="text"
                            className="form-input"
                            value={subject}
                            onChange={(e) => setSubject(e.target.value)}
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Body</label>
                        <textarea
                            id="email-body"
                            className="form-textarea"
                            rows={14}
                            value={body}
                            onChange={(e) => setBody(e.target.value)}
                        />
                    </div>

                    {result && (
                        <div className={`modal-result ${result.type}`}>
                            {result.type === 'success' ? '✅' : '❌'} {result.message}
                        </div>
                    )}
                </div>

                <div className="modal-footer">
                    <button className="btn-cancel" onClick={onClose}>
                        Cancel
                    </button>
                    <button
                        id="send-email-btn"
                        className="btn-send"
                        onClick={handleSend}
                        disabled={sending}
                    >
                        {sending ? (
                            <><span className="spinner"></span> Sending…</>
                        ) : (
                            <>📤 Send Email</>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
