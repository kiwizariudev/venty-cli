async function sendCommand(cmd) {
    const response = await fetch('http://localhost:8888/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd })
    });
    const data = await response.json();
    console.log("Venty Response:", data);
}

sendCommand("hello from JavaScript");
