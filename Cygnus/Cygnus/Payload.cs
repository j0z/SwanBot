using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using System.Threading.Tasks;

namespace Cygnus
{
    public class Payload
    {
        public enum Param
        {
            user_value,
            find_nodes,
            get_nodes,
            create_node,
            delete_nodes
        }

        Param param { get; set; }
        string query { get; set; }
        string type { get; set; }
        bool isPublic { get; set; }
        string filter { get; set; }
        string apikey { get; set; }

        JsonSerializerSettings jsonsettings = new JsonSerializerSettings { NullValueHandling = NullValueHandling.Ignore } ;

        /// <summary>
        /// Serializes the Payload object into a valid JSON string if no arguments are supplied, otherwise converts the arguments into a JSON string
        /// WARNING! defaults to isPublic=TRUE!
        /// </summary>
        /// <param name="param"></param>
        /// <param name="query"></param>
        /// <param name="type"></param>
        /// <param name="isPublic"></param>
        /// <param name="filter"></param>
        /// <param name="apikey"></param>
        /// <returns></returns>
        public string PackagePayload(Param param, string query =null, string type=null, bool isPublic=true, string filter=null, string apikey=null)
        {
            this.param = param;
            this.query = query;
            this.type = type;
            this.isPublic = isPublic;
            this.filter = filter;
            this.apikey = apikey;
            return JsonConvert.SerializeObject(this, jsonsettings);
        }

        public string PackagePayload()
        {
            return JsonConvert.SerializeObject(this, jsonsettings);
        }
    }
}
