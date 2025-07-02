# chatify
Γενική Περιγραφή

Το Chatify είναι ένα real-time chat app χχισμένη με FastAPI + WebSockets + PostgreSQL + Docker + Kubernetes. 

##Λειτουργία:

###Login / Signup
Κατάχωρηση χρήστη / εγγραφή μέσω φορμές
Δεν γίνεται hashing password (για απλότητα demo)
Session stored στο SessionMiddleware
Δεν υπάρχει external auth service

###Real-time Messaging
WebSocket @ /ws/{username}
Αποστολή & λήψη μηνυμάτων μεταξύ 2 χρηστών
Αποθήκευση στο PostgreSQL 
Ανάγνωση / read=true όταν ανοιχθεί η συνομιλία

###Fetch APIs
/messages/{sender}/{receiver} : Όλα τα μηνύματα
/unread_counts/{username} : Πόσα μηνύματα αδιάβαστα ανά user
/online : Λίστα με τους online χρήστες
/get_users : Όλοι οι χρήστες εκτός από εσένα

##Deployment:

git clone https://github.com/vtheofil/chatify.git
cd chatify

 Δημιουργία .env
 DATABASE_URL=postgresql://chatuser:admin123@db:5432/chatdb

 Build image (Docker)
 docker build -t chatify .
 docker-compose up --build
 Web app: http://localhost:8000

##Kubernetes Setup:
kubectl apply -f db-deployment.yaml
kubectl apply -f db-service.yaml
kubectl apply -f postgres-pvc.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml

##Load Tester (για autoscaling):
ΓΙΑ ΑUTOSCALLING 
kubectl run load-tester --image=busybox --restart=Never -it -- \
/bin/sh -c "while true; do wget -q -O - http://chatify-service; done"
kubectl get hpa
kubectl get pods : και παρατηρούμε αν αυξάνονται τα pods 
Έπειτα κάνουμε delete τον load-tester 

####Database Structure

##PostgreSQL DB: chatdb

chatdb=> \d users
                                        Table "public.users"
   Column   |            Type             | Collation | Nullable |              Default
------------+-----------------------------+-----------+----------+-----------------------------------
 id         | integer                     |           | not null | nextval('users_id_seq'::regclass)
 username   | character varying(50)       |           | not null |
 password   | text                        |           | not null |
 is_online  | boolean                     |           |          | false
 created_at | timestamp without time zone |           |          | CURRENT_TIMESTAMP
 
chatdb=> \d messages
Column   |            Type             | Collation | Nullable |               Default
-----------+-----------------------------+-----------+----------+--------------------------------------
 id        | integer                     |           | not null | nextval('messages_id_seq'::regclass)
 sender    | character varying           |           | not null |
 receiver  | character varying           |           | not null |
 content   | text                        |           | not null |
 timestamp | timestamp without time zone |           |          |
 read      | boolean                     |           |          | false 

 chatdb=> \d sessions
                                        Table "public.sessions"
   Column   |            Type             | Collation | Nullable |               Default
------------+-----------------------------+-----------+----------+--------------------------------------
 id         | integer                     |           | not null | nextval('sessions_id_seq'::regclass)
 user_id    | integer                     |           |          |
 token      | text                        |           | not null |
 created_at | timestamp without time zone |           |          | CURRENT_TIMESTAMP
 expires_at | timestamp without time zone |           |          |



