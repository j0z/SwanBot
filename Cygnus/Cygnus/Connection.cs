using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net;
using Windows.Networking;
using Windows.Networking.Sockets;
using Windows.Storage.Streams;
namespace Cygnus
{
    public class Connection
    {

        public string server { get; set; }
        string port { get; set; }
        string APIkey
        {
            get
            {
                return APIkey;
            }

            set
            {
                this.APIkey = "934a26c6ec10c1c44e1e140c6ffa25036166c0afd0efcfe638693e6a";
            }
        }

        public string ServerResponse;
        private StreamSocket streamSocket;

        /// <summary>
        /// Connects to the specified Swanbot server
        /// </summary>
        /// <param name="addr"></param>
        /// <param name="port"></param>
        /// <returns></returns>
        public async void Connect(string addr, string port)
        {
            this.server = addr;
            this.port = port;

            StreamSocket Socket = streamSocket;

            if (Socket == null)
            {
                HostName hostName = new HostName(server);
                Socket = new StreamSocket();

                await Socket.ConnectAsync(hostName, this.port);
                streamSocket = Socket;
            }
        }

        public bool Disconnect()
        {
            throw new NotImplementedException();
        }

        public void send(string msg)
        {
            sendAll("api-send:"+msg + "\\r\\n");
        }


        public void get(string msg)
        {
            sendAll("api-get:" + msg + "\\r\\n");
            waitResponse();
        }

        private async void sendAll(string payload)
        {
            Connect(server, port);
            
            DataWriter writer = new DataWriter(streamSocket.OutputStream);
            UInt32 len = writer.MeasureString(payload);

            await writer.StoreAsync();
            writer.DetachStream();
            writer.Dispose();
        }

        private async void waitResponse()
        {
            Connect(server, port);

            DataReader reader = new DataReader(streamSocket.InputStream);
            UInt32 len = reader.UnconsumedBufferLength;
            await reader.LoadAsync(len);

            while (reader.UnconsumedBufferLength > 0)
            {
                uint bytesToRead = reader.ReadUInt32();
                ServerResponse += reader.ReadString(bytesToRead);
            }
            reader.DetachStream();
            reader.Dispose();
        }
    }
}
