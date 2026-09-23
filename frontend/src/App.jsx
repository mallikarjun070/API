import { useMemo, useState } from 'react';

const initialForm = {
  fullName: 'Aisha Thompson',
  email: 'aisha.thompson@email.com',
  phone: '+1 (415) 555-0148',
  location: 'San Francisco, CA',
  targetRole: 'Senior Product Designer',
  summary:
    'Product designer with 6+ years of experience creating intuitive digital experiences for SaaS products and mobile apps. Skilled in user research, design systems, and cross-functional collaboration to turn complex workflows into clear, high-converting experiences.',
  skills: 'UX Research, Figma, Design Systems, User Flows, Prototyping, A/B Testing, Wireframing, Accessibility',
  experience:
    'Lead Product Designer | Northstar Labs\nDesigned and launched a multi-product design system used across 4 web applications, improving design consistency and reducing handoff time by 35%.\nPartnered with engineering and marketing teams to define UX strategy for onboarding flows, resulting in a 22% increase in activation.\n\nSenior UX Designer | Beacon Studio\nCreated responsive product interfaces for B2B and healthcare clients, translating business goals into user-centered experiences and prototypes validated by usability testing.',
  education:
    'B.A. in Interaction Design\nUniversity of California, Davis\n2016',
};

function App() {
  const [form, setForm] = useState(initialForm);
  const [status, setStatus] = useState('Preview ready');

  const skills = useMemo(
    () =>
      form.skills
        .split(',')
        .map((skill) => skill.trim())
        .filter(Boolean),
    [form.skills],
  );

  const experience = useMemo(
    () =>
      form.experience
        .split('\n\n')
        .map((entry) => entry.trim())
        .filter(Boolean),
    [form.experience],
  );

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleGenerate = async () => {
    const apiUrl = import.meta.env.VITE_API_URL;

    if (!apiUrl) {
      setStatus('Local preview mode is active. Add VITE_API_URL to connect a backend.');
      return;
    }

    try {
      setStatus('Generating resume draft...');
      const response = await fetch(`${apiUrl}/resume/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        throw new Error('Unable to generate resume from backend.');
      }

      const data = await response.json();
      setStatus(data.message || 'Resume updated successfully.');
    } catch (error) {
      setStatus(error.message || 'Something went wrong while generating the resume.');
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Career toolkit</p>
          <h1>AI Resume Builder</h1>
        </div>
        <button type="button" className="primary-btn" onClick={handleGenerate}>
          Generate Resume Draft
        </button>
      </header>

      <div className="workspace">
        <aside className="panel form-panel">
          <div className="field-group">
            <label htmlFor="fullName">Full name</label>
            <input id="fullName" name="fullName" value={form.fullName} onChange={handleChange} />
          </div>

          <div className="two-columns">
            <div className="field-group">
              <label htmlFor="email">Email</label>
              <input id="email" name="email" value={form.email} onChange={handleChange} />
            </div>
            <div className="field-group">
              <label htmlFor="phone">Phone</label>
              <input id="phone" name="phone" value={form.phone} onChange={handleChange} />
            </div>
          </div>

          <div className="two-columns">
            <div className="field-group">
              <label htmlFor="location">Location</label>
              <input id="location" name="location" value={form.location} onChange={handleChange} />
            </div>
            <div className="field-group">
              <label htmlFor="targetRole">Target role</label>
              <input id="targetRole" name="targetRole" value={form.targetRole} onChange={handleChange} />
            </div>
          </div>

          <div className="field-group">
            <label htmlFor="summary">Professional summary</label>
            <textarea id="summary" name="summary" rows="5" value={form.summary} onChange={handleChange} />
          </div>

          <div className="field-group">
            <label htmlFor="skills">Skills</label>
            <textarea id="skills" name="skills" rows="3" value={form.skills} onChange={handleChange} />
          </div>

          <div className="field-group">
            <label htmlFor="experience">Experience</label>
            <textarea id="experience" name="experience" rows="8" value={form.experience} onChange={handleChange} />
          </div>

          <div className="field-group">
            <label htmlFor="education">Education</label>
            <textarea id="education" name="education" rows="4" value={form.education} onChange={handleChange} />
          </div>
        </aside>

        <main className="panel preview-panel">
          <div className="resume-card">
            <header className="resume-header">
              <div>
                <h2>{form.fullName}</h2>
                <p>{form.targetRole}</p>
              </div>
              <div className="contact-list">
                <span>{form.email}</span>
                <span>{form.phone}</span>
                <span>{form.location}</span>
              </div>
            </header>

            <section className="resume-section">
              <h3>Professional Summary</h3>
              <p>{form.summary}</p>
            </section>

            <section className="resume-section">
              <h3>Skills</h3>
              <div className="skill-list">
                {skills.map((skill) => (
                  <span key={skill} className="skill-chip">
                    {skill}
                  </span>
                ))}
              </div>
            </section>

            <section className="resume-section">
              <h3>Experience</h3>
              {experience.map((entry) => {
                const lines = entry.split('\n');
                const title = lines[0] || 'Role';
                const details = lines.slice(1);

                return (
                  <div key={`${title}-${entry}`} className="job-block">
                    <h4>{title}</h4>
                    <ul>
                      {details.map((detail) => (
                        <li key={detail}>{detail}</li>
                      ))}
                    </ul>
                  </div>
                );
              })}
            </section>

            <section className="resume-section">
              <h3>Education</h3>
              <p>{form.education}</p>
            </section>
          </div>
        </main>
      </div>

      <div className="status-bar" aria-live="polite">
        {status}
      </div>
    </div>
  );
}

export default App;
