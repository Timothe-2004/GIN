import React, { useState } from 'react';

function AddPartenaire() {
  const [name, setName] = useState('');
  const [website, setWebsite] = useState('');
  const [message, setMessage] = useState('');

  const handleAddPartenaire = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://127.0.0.1:8000/api/partenaires/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          nom: name,
          site_web: website,
        }),
      });

      if (response.ok) {
        setMessage('Partenaire added successfully!');
      } else {
        setMessage('Failed to add partenaire.');
      }
    } catch (error) {
      setMessage('An error occurred. Please try again later.');
    }
  };

  return (
    <div>
      <h2>Add Partenaire</h2>
      <form onSubmit={handleAddPartenaire}>
        <div>
          <label>Name:</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Website:</label>
          <input
            type="url"
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
            required
          />
        </div>
        <button type="submit">Add Partenaire</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default AddPartenaire;