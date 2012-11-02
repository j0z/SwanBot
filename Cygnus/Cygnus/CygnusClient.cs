using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json.Serialization;



namespace Cygnus
{
    public class CygnusClient
    {
        public List<Connection> Servers = new List<Connection>();

        Payload payload = new Payload();

        public bool AddServer(string server, string port, string apiKey)
        {
            Connection connection = new Connection();

            connection.Connect(server, port);
            Servers.Add(connection);
            return true;
        }

        public string get(int index, Payload payload)
        {
            Connection server = Servers.ElementAt(index);
            server.get(payload.PackagePayload());

            return server.ServerResponse;
        }

        public void set(int index, Payload payload)
        {
            Connection server = Servers.ElementAt(index);
            server.send(payload.PackagePayload());
        }

        public void createNode(int index, string query)
        {
            Connection server = Servers.ElementAt(index);
            server.send(payload.PackagePayload(Payload.Param.create_node, query));
        }

        public string findNode(int index, string query)
        {
            Connection server = Servers.ElementAt(index);
            server.get(payload.PackagePayload(Payload.Param.find_nodes, query));
            return server.ServerResponse;
        }


        /// <summary>
        /// <nodes> should be in the format [int,int,int]
        /// </summary>
        /// <param name="server"></param>
        /// <param name="?"></param>
        public void getNodes(Connection server, string nodes)
        {
            throw new NotImplementedException();

            //server.get(payload.PackagePayload(Payload.Param.get_nodes, null, null, true, 
        }
    }
}
