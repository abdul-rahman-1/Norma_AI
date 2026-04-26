You are fixing logging in a FastAPI backend deployed on Render that integrates Twilio WhatsApp.

-------------------------------------
PROBLEM
-------------------------------------

Logging is implemented across the system, but logs are not appearing in the Render terminal during runtime when handling requests.

Startup logs appear correctly, but logs inside request handling (webhook, services, database) are missing.

-------------------------------------
ROOT CAUSES
-------------------------------------

1. Root logger handlers are being cleared:
   root_logger.handlers.clear()
   This removes Uvicorn's default logging configuration required for Render logs.

2. Multiple logger instances are created inconsistently:
   - logging.getLogger()
   - logging.getLogger(name)

   Handlers are reset or removed, causing logs to not propagate.

3. Logging is not guaranteed to use stdout, which Render depends on.

4. Logging is not executed at the earliest point in webhook handling.

5. Uvicorn logging system is being overridden incorrectly.

-------------------------------------
DATABASE CONTEXT (FULL SCHEMA)
-------------------------------------

The system uses two logical database partitions:

1. PHI Database → clinic_[ID]_phi  
2. Profile Database → clinic_[ID]_profile  

-------------------------------------
PHI DATABASE COLLECTIONS
-------------------------------------

1. patients  
- patient_uuid  
- full_name  
- phone_number (UNIQUE)  
- email  
- date_of_birth  
- gender  
- address  
- emergency_contact_name  
- emergency_contact_phone  
- medical_alerts  
- insurance_provider  
- insurance_id  
- notes  
- created_at  
- updated_at  
- is_active  

2. appointments  
- appointment_uuid  
- patient_id (FK)  
- doctor_id (FK)  
- appointment_datetime  
- duration_minutes  
- appointment_type  
- status (scheduled, confirmed, completed, cancelled, no_show)  
- cancellation_reason  
- chief_complaint  
- diagnosis  
- treatment_plan  
- prescription (JSON)  
- lab_orders (JSON)  
- follow_up_required  
- follow_up_date  
- reminder_sent  
- confirmed_by_patient  
- source (whatsapp, voice, dashboard)  
- created_at  

3. medical_records  
- record_uuid  
- patient_id  
- appointment_id  
- record_type  
- title  
- content  
- structured_data (JSON)  
- attachments  
- doctor_id  

4. prescriptions  
- prescription_uuid  
- patient_id  
- appointment_id  
- doctor_id  
- medications (JSON)  
- pharmacy_name  
- filled_status  
- refill_allowed  

5. insurance_claims  
- claim_uuid  
- patient_id  
- appointment_id  
- insurance_provider  
- claim_amount  
- claim_status  

6. patient_communications  
- communication_uuid  
- patient_id  
- communication_type (whatsapp, sms, voice)  
- direction (inbound, outbound)  
- channel_identifier  
- message_content  
- intent_detected  
- norma_response  
- action_taken  
- sentiment  
- conversation_thread_id  
- timestamp  

-------------------------------------
PROFILE DATABASE COLLECTIONS
-------------------------------------

7. clinic_info  
- clinic_uuid  
- clinic_name  
- phone  
- whatsapp_number  
- address  
- timezone  
- subscription_plan  

8. doctors  
- doctor_uuid  
- full_name  
- specialty  
- whatsapp_number  
- consultation_fee  
- is_active  

9. operating_hours  
- doctor_id  
- day_of_week  
- open_time  
- close_time  

10. staff_users  
- user_uuid  
- full_name  
- email  
- phone  
- role  
- password_hash  

11. response_templates  
- template_uuid  
- name  
- category  
- text_en  
- variables  

12. activity_log  
- activity_uuid  
- action_type  
- source  
- entity_type  
- entity_id  
- description  
- result  

13. system_integrations  
- integration_uuid  
- integration_type  
- system_name  
- api_endpoint  
- connection_status  

14. norma_preferences  
- preference_category  
- preference_key  
- preference_value  

15. notifications  
- notification_uuid  
- recipient_staff_id  
- notification_type  
- priority  
- message  

16. billing_transactions  
- transaction_uuid  
- transaction_type  
- amount  
- status  

17. analytics_snapshots  
- snapshot_date  
- total_appointments  
- new_patients  
- revenue_generated  

18. audit_log  
- audit_uuid  
- user_id  
- action  
- resource_type  
- status_code  
- timestamp  

-------------------------------------
GOAL
-------------------------------------

Fix the logging system so that:

- Logs appear in Render during runtime
- Logs from webhook, services, and DB operations are visible
- Logs are consistent across all modules
- Logging integrates correctly with FastAPI and Uvicorn
- No logs are lost due to handler misconfiguration

-------------------------------------
SCOPE
-------------------------------------

- Fix logger configuration
- Fix handler usage
- Fix propagation behavior
- Ensure logs go to stdout
- Ensure compatibility with Uvicorn logging
- Ensure logging works across all database interactions and request flows

-------------------------------------
OUTPUT
-------------------------------------

Return corrected logging setup so logs are reliably visible in Render logs across all modules and database operations.