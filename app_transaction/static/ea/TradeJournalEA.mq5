#property strict
#property version   "1.0"

input string API_BASE_URL = "https://trade.piqagram.ir";
input string API_KEY      = "";
input int    HEARTBEAT_SECONDS = 30;
input int    SYNC_SECONDS      = 60;
input int    HISTORY_DAYS      = 365;

datetime last_heartbeat = 0;
datetime last_sync = 0;


// ============================================================
// URL
// ============================================================

string GetURL(string endpoint)
{
   return API_BASE_URL + endpoint;
}


// ============================================================
// JSON helpers
// ============================================================

string JsonEscape(string value)
{
   StringReplace(value, "\\", "\\\\");
   StringReplace(value, "\"", "\\\"");
   StringReplace(value, "\r", "\\r");
   StringReplace(value, "\n", "\\n");
   StringReplace(value, "\t", "\\t");

   return value;
}


string TimeToISO(datetime t)
{
   MqlDateTime dt;
   TimeToStruct(t, dt);

   return StringFormat(
      "%04d-%02d-%02dT%02d:%02d:%02dZ",
      dt.year,
      dt.mon,
      dt.day,
      dt.hour,
      dt.min,
      dt.sec
   );
}


// ============================================================
// HTTP POST
// ============================================================

bool SendPOST(string endpoint, string json, string &response)
{
   string url = GetURL(endpoint);

   string headers =
      "Content-Type: application/json\r\n"
      "X-API-Key: " + API_KEY + "\r\n";

   char post[];
   char result[];

   StringToCharArray(json, post, 0, WHOLE_ARRAY, CP_UTF8);

   ResetLastError();

   int status = WebRequest(
      "POST",
      url,
      headers,
      10000,
      post,
      result,
      headers
   );

   if(status == -1)
   {
      Print(
         "WebRequest failed. Error: ",
         GetLastError()
      );

      return false;
   }

   response = CharArrayToString(
      result,
      0,
      -1,
      CP_UTF8
   );

   Print(
      "POST ",
      endpoint,
      " -> HTTP ",
      status,
      " | ",
      response
   );

   return status >= 200 && status < 300;
}


// ============================================================
// HEARTBEAT
// ============================================================

bool SendHeartbeat()
{
   string json = StringFormat(
      "{\"account_number\":\"%I64d\",\"server\":\"%s\",\"platform\":\"mt5\"}",
      AccountInfoInteger(ACCOUNT_LOGIN),
      JsonEscape(AccountInfoString(ACCOUNT_SERVER))
   );

   string response;

   return SendPOST(
      "/app/settings/metatrader/heartbeat/",
      json,
      response
   );
}


// ============================================================
// CONNECT
// ============================================================

bool SendConnect()
{
   string json = StringFormat(
      "{\"platform\":\"mt5\",\"server\":\"%s\",\"account_number\":\"%I64d\"}",
      JsonEscape(AccountInfoString(ACCOUNT_SERVER)),
      AccountInfoInteger(ACCOUNT_LOGIN)
   );

   string response;

   return SendPOST(
      "/app/settings/metatrader/connect/",
      json,
      response
   );
}


// ============================================================
// OPEN POSITIONS
// ============================================================

void AddOpenPosition(
   string &json,
   bool &first,
   ulong ticket
)
{
   if(!PositionSelectByTicket(ticket))
      return;

   string symbol = PositionGetString(POSITION_SYMBOL);

   ENUM_POSITION_TYPE position_type =
      (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);

   double volume =
      PositionGetDouble(POSITION_VOLUME);

   double entry_price =
      PositionGetDouble(POSITION_PRICE_OPEN);

   double stop_loss =
      PositionGetDouble(POSITION_SL);

   double take_profit =
      PositionGetDouble(POSITION_TP);

   double profit =
      PositionGetDouble(POSITION_PROFIT);

   datetime open_time =
      (datetime)PositionGetInteger(POSITION_TIME);

   string type;

   if(position_type == POSITION_TYPE_BUY)
      type = "buy";
   else
      type = "sell";

   if(!first)
      json += ",";

   first = false;

   json += StringFormat(
      "{"
      "\"mt_ticket\":\"%I64u\","
      "\"symbol\":\"%s\","
      "\"transaction_type\":\"%s\","
      "\"entry_price\":%.8f,"
      "\"exit_price\":null,"
      "\"volume\":%.8f,"
      "\"profit_loss\":%.2f,"
      "\"stop_loss\":%.8f,"
      "\"take_profit\":%.8f,"
      "\"closed_at\":null,"
      "\"opened_at\":\"%s\""
      "}",
      ticket,
      JsonEscape(symbol),
      type,
      entry_price,
      volume,
      profit,
      stop_loss,
      take_profit,
      TimeToISO(open_time)
   );
}


// ============================================================
// HISTORY
// ============================================================

bool GetEntryDeal(
   ulong position_id,
   double &entry_price,
   double &volume,
   ENUM_DEAL_TYPE &deal_type,
   datetime &open_time
)
{
   entry_price = 0;
   volume = 0;
   open_time = 0;

   if(!HistorySelectByPosition(position_id))
      return false;

   int total = HistoryDealsTotal();

   for(int i = 0; i < total; i++)
   {
      ulong ticket = HistoryDealGetTicket(i);

      if(ticket == 0)
         continue;

      ENUM_DEAL_ENTRY entry =
         (ENUM_DEAL_ENTRY)HistoryDealGetInteger(
            ticket,
            DEAL_ENTRY
         );

      if(entry != DEAL_ENTRY_IN &&
         entry != DEAL_ENTRY_INOUT)
         continue;

      entry_price =
         HistoryDealGetDouble(
            ticket,
            DEAL_PRICE
         );

      volume =
         HistoryDealGetDouble(
            ticket,
            DEAL_VOLUME
         );

      deal_type =
         (ENUM_DEAL_TYPE)HistoryDealGetInteger(
            ticket,
            DEAL_TYPE
         );

      open_time =
         (datetime)HistoryDealGetInteger(
            ticket,
            DEAL_TIME
         );

      return true;
   }

   return false;
}


// ============================================================
// CLOSED TRADES
// ============================================================

void AddClosedDeal(
   string &json,
   bool &first,
   ulong ticket
)
{
   if(!HistoryDealSelect(ticket))
      return;

   ENUM_DEAL_ENTRY entry =
      (ENUM_DEAL_ENTRY)HistoryDealGetInteger(
         ticket,
         DEAL_ENTRY
      );

   if(entry != DEAL_ENTRY_OUT &&
      entry != DEAL_ENTRY_OUT_BY)
      return;

   ulong position_id =
      (ulong)HistoryDealGetInteger(
         ticket,
         DEAL_POSITION_ID
      );

   string symbol =
      HistoryDealGetString(
         ticket,
         DEAL_SYMBOL
      );

   double exit_price =
      HistoryDealGetDouble(
         ticket,
         DEAL_PRICE
      );

   double volume =
      HistoryDealGetDouble(
         ticket,
         DEAL_VOLUME
      );

   double profit =
      HistoryDealGetDouble(
         ticket,
         DEAL_PROFIT
      );

   double commission =
      HistoryDealGetDouble(
         ticket,
         DEAL_COMMISSION
      );

   double swap =
      HistoryDealGetDouble(
         ticket,
         DEAL_SWAP
      );

   datetime closed_at =
      (datetime)HistoryDealGetInteger(
         ticket,
         DEAL_TIME
      );

   double entry_price;
   double entry_volume;
   ENUM_DEAL_TYPE entry_type;
   datetime open_time;

   if(!GetEntryDeal(
      position_id,
      entry_price,
      entry_volume,
      entry_type,
      open_time
   ))
   {
      return;
   }

   string transaction_type;

   if(entry_type == DEAL_TYPE_BUY)
      transaction_type = "buy";
   else
      transaction_type = "sell";

   double total_profit =
      profit + commission + swap;

   if(!first)
      json += ",";

   first = false;

   json += StringFormat(
      "{"
      "\"mt_ticket\":\"%I64u\","
      "\"mt_position_id\":\"%I64u\","
      "\"symbol\":\"%s\","
      "\"transaction_type\":\"%s\","
      "\"entry_price\":%.8f,"
      "\"exit_price\":%.8f,"
      "\"volume\":%.8f,"
      "\"profit_loss\":%.2f,"
      "\"closed_at\":\"%s\","
      "\"opened_at\":\"%s\""
      "}",
      ticket,
      position_id,
      JsonEscape(symbol),
      transaction_type,
      entry_price,
      exit_price,
      volume,
      total_profit,
      TimeToISO(closed_at),
      TimeToISO(open_time)
   );
}


// ============================================================
// SYNC TRANSACTIONS
// ============================================================

bool SyncTransactions()
{
   string json = "{\"transactions\":[";

   bool first = true;

   // ---------------------------------------------------------
   // Open positions
   // ---------------------------------------------------------

   int positions_total =
      PositionsTotal();

   for(int i = 0; i < positions_total; i++)
   {
      ulong ticket =
         PositionGetTicket(i);

      if(ticket == 0)
         continue;

      AddOpenPosition(
         json,
         first,
         ticket
      );
   }


   // ---------------------------------------------------------
   // Closed history
   // ---------------------------------------------------------

   datetime from =
      TimeCurrent() -
      (HISTORY_DAYS * 86400);

   datetime to =
      TimeCurrent();

   if(HistorySelect(from, to))
   {
      int deals_total =
         HistoryDealsTotal();

      for(int i = 0; i < deals_total; i++)
      {
         ulong ticket =
            HistoryDealGetTicket(i);

         if(ticket == 0)
            continue;

         AddClosedDeal(
            json,
            first,
            ticket
         );
      }
   }

   json += "]}";

   string response;

   return SendPOST(
      "/app/settings/metatrader/sync-transactions/",
      json,
      response
   );
}


// ============================================================
// INITIALIZATION
// ============================================================

int OnInit()
{
   Print("TradeJournal EA started.");

   if(StringLen(API_KEY) == 0)
   {
      Print("ERROR: API_KEY is empty.");

      return INIT_PARAMETERS_INCORRECT;
   }

   EventSetTimer(10);

   SendConnect();
   SendHeartbeat();
   SyncTransactions();

   last_heartbeat =
      TimeCurrent();

   last_sync =
      TimeCurrent();

   return INIT_SUCCEEDED;
}


// ============================================================
// DEINITIALIZATION
// ============================================================

void OnDeinit(const int reason)
{
   EventKillTimer();

   Print(
      "TradeJournal EA stopped. Reason: ",
      reason
   );
}


// ============================================================
// TIMER
// ============================================================

void OnTimer()
{
   datetime now =
      TimeCurrent();


   // Heartbeat
   if(now - last_heartbeat >= HEARTBEAT_SECONDS)
   {
      SendHeartbeat();

      last_heartbeat = now;
   }


   // Transaction sync
   if(now - last_sync >= SYNC_SECONDS)
   {
      SyncTransactions();

      last_sync = now;
   }
}


// ============================================================
// TRADE EVENT
// ============================================================

void OnTradeTransaction(
   const MqlTradeTransaction &trans,
   const MqlTradeRequest &request,
   const MqlTradeResult &result
)
{
   if(trans.type == TRADE_TRANSACTION_DEAL_ADD)
   {
      // معامله جدید یا بسته‌شدن معامله
      // کمی تأخیر می‌دهیم تا History کامل ثبت شود.
      Sleep(500);

      SyncTransactions();
   }
}