import React, { useState } from 'react';

function AddRealisation() {
  const [project, setProject] = useState('');
  const [company, setCompany] = useState('');
  const [review, setReview] = useState('');
  const [personType, setPersonType] = useState('');
  const [message, setMessage] = useState('');

  const handleAddRealisation = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://127.0.0.1:8000/api/realisations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          projet: project,
          entreprise: company,
          avis: review,
          type_personne: personType,
        }),
      });

      if (response.ok) {
        setMessage('Realisation added successfully!');
      } else {
        setMessage('Failed to add realisation.');
      }
    } catch (error) {
      setMessage('An error occurred. Please try again later.');
    }
  };

  return (
    <div>
      <h2>Add Realisation</h2>
      <form onSubmit={handleAddRealisation}>
        <div>
          <label>Project:</label>
          <input
            type="text"
            value={project}
            onChange={(e) => setProject(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Company:</label>
          <input
            type="text"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Review:</label>
          <textarea
            value={review}
            onChange={(e) => setReview(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Person Type:</label>
          <input
            type="text"
            value={personType}
            onChange={(e) => setPersonType(e.target.value)}
            required
          />
        </div>
        <button type="submit">Add Realisation</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default AddRealisation;