export default function ResumeSummaryCard({ profile }) {
    return (
        <div className="resume-summary">
            <div className="summary-section">
                <div className="summary-label">Skills</div>
                <div className="tag-list">
                    {profile.skills.map((skill, i) => (
                        <span key={i} className="tag">{skill}</span>
                    ))}
                </div>
            </div>

            <div className="summary-section">
                <div className="summary-label">Domains</div>
                <div className="tag-list">
                    {profile.domains.map((domain, i) => (
                        <span key={i} className="tag tag-accent">{domain}</span>
                    ))}
                </div>
            </div>

            <div className="summary-row">
                <div className="summary-section">
                    <div className="summary-label">Experience Level</div>
                    <span className="tag tag-success">{profile.experience_level}</span>
                </div>
                <div className="summary-section">
                    <div className="summary-label">Preferred Roles</div>
                    <div className="tag-list">
                        {profile.preferred_roles.map((role, i) => (
                            <span key={i} className="tag tag-accent">{role}</span>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
