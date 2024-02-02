        var term = new Terminal();
        term.open(document.getElementById('terminal'));
        const fitAddon = new FitAddon.FitAddon();
        term.loadAddon(fitAddon);
        fitAddon.fit();

        // Enable fit on the terminal whenever the window is resized
        window.addEventListener('resize', () => {
            fitAddon.fit();
            try {

              size_dim = 'cols:' +  term.cols + '::rows:' + term.rows;


            console.log("front end window resize event: " + size_dim);
            backend.set_pty_size(size_dim);
            } catch (error) {
              console.error(error);
              console.log("Channel may not be up yet!")

            }
        });

        // When data is entered into the terminal, send it to the backend
        term.onData(e => {
        // console.log(e);
            backend.write_data(e);

        });

        // Function to handle incoming data from the backend
        window.handle_output = function(data) {
            term.write(data);
        };

        // Establish a connection with the Qt backend
        new QWebChannel(qt.webChannelTransport, function(channel) {
            window.backend = channel.objects.backend;
        });

        window.onload = function() {

        term.focus();
        term.setOption('theme', {
  background: '#141414' // Replace with your desired color
});
let style = document.createElement('style');
style.innerHTML = `
.xterm-viewport::-webkit-scrollbar {
    width: 12px;
}

.xterm-viewport::-webkit-scrollbar-track {
    background: #212121;
}

.xterm-viewport::-webkit-scrollbar-thumb {
    background: #888;
}

.xterm-viewport::-webkit-scrollbar-thumb:hover {
    background: #555;
}`;

document.head.appendChild(style);
//        term.write("Press Enter To Begin...") // not needed now that xterm.js and pty sizes in sync


};
