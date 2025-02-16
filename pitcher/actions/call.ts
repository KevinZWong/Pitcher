"use server"

export default async function callApi(values) {
    const response = await fetch('http://localhost:5000/api/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: values.prompt,
          githubUrl: values.githubLink,
          driveUrl: values.driveLink
        }),
      });
      
      if (!response.ok) throw new Error('Failed to create project');

      const data = await response.json();
      return data;
    }