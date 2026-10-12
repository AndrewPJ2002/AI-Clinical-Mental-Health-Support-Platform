# chat routes

'''
1. React sends a message.

2. Backend checks the JWT and identifies the user.

3. Backend checks the chat belongs to that user.

4. Backend checks for crisis language.

5. If crisis: return the safe crisis response.

6. If not crisis: call OpenAI with conversation history.

7. Save both messages in PostgreSQL.

8. Return the assistant reply to React.

'''