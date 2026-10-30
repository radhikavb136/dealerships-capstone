import { useState } from "react";

const initialValues = { username: "", firstName: "", lastName: "", email: "", password: "" };

export default function Register({ onRegistered }) {
  const [values, setValues] = useState(initialValues);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function update(event) {
    setValues((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function submit(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    if (values.password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setBusy(true);
    try {
      const response = await fetch("/djangoapp/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userName: values.username,
          firstName: values.firstName,
          lastName: values.lastName,
          email: values.email,
          password: values.password,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Registration failed.");
      setMessage("Account created. You can now log in.");
      setValues(initialValues);
      if (onRegistered) onRegistered(data);
    } catch (err) {
      setError(err.message || "Unable to register right now.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="form-card" onSubmit={submit}>
      <h2>Create your account</h2>
      <label>Username<input name="username" value={values.username} onChange={update} autoComplete="username" required minLength={3} /></label>
      <label>First Name<input name="firstName" value={values.firstName} onChange={update} autoComplete="given-name" required /></label>
      <label>Last Name<input name="lastName" value={values.lastName} onChange={update} autoComplete="family-name" required /></label>
      <label>Email<input type="email" name="email" value={values.email} onChange={update} autoComplete="email" required /></label>
      <label>Password<input type="password" name="password" value={values.password} onChange={update} autoComplete="new-password" minLength={8} required /></label>
      <button type="submit" disabled={busy}>{busy ? "Creating account…" : "Register"}</button>
      {message && <p className="success" role="status">{message}</p>}
      {error && <p className="error" role="alert">{error}</p>}
    </form>
  );
}
