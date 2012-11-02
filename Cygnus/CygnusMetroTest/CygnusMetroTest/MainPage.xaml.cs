using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Windows.Foundation;
using Windows.Foundation.Collections;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Xaml.Controls.Primitives;
using Windows.UI.Xaml.Data;
using Windows.UI.Xaml.Input;
using Windows.UI.Xaml.Media;
using Windows.UI.Xaml.Navigation;
using Cygnus;

// The Blank Page item template is documented at http://go.microsoft.com/fwlink/?LinkId=234238

namespace CygnusMetroTest
{
    /// <summary>
    /// An empty page that can be used on its own or navigated to within a Frame.
    /// </summary>
    public sealed partial class MainPage : Page
    {
        string ServerIP;
        string ServerPort;

        CygnusClient client = new CygnusClient();

        public MainPage()
        {
            this.InitializeComponent();
        }

        /// <summary>
        /// Invoked when this page is about to be displayed in a Frame.
        /// </summary>
        /// <param name="e">Event data that describes how this page was reached.  The Parameter
        /// property is typically used to configure the page.</param>
        protected override void OnNavigatedTo(NavigationEventArgs e)
        {
        }

        private void Connect_Btn_Click(object sender, RoutedEventArgs e)
        {
            ServerIP = IPAddress_Box.Text;
            ServerPort = Port_Box.Text;

            bool isConnected = client.AddServer(ServerIP, ServerPort, ""); //Pass a blank string as the API, because Swanbot/Cygnus currently uses a hardcoded key for testing

            if (isConnected)
                ConnectionStatus_Text.Text = "Connected!";
        }

        private void GetNode_Btn_Click(object sender, RoutedEventArgs e)
        {
            findNode_Text.Text = client.findNode(client.Servers.ElementAt(0), Node_Box.Text);
        }
    }
}
