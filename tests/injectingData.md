In order to inject data, you pass in a dictionary.
Each area (if present) contains a list of data to inject

* visits
  * start (python datetime object)
  * leave (python datetime ojbect) - (optional for "In" and "Forgot")
  * barcode
  * status (One of: "In", "Out", "Forgot")
* members
  * barcode
  * displayName
  * firstName
  * lastName
  * email
  * membershipExpires (python datetime object)
* guests
  * guest_id
  * displayName
  * email
  * firstName
  * lastName
  * whereFound  (free flow text)
  * status (1 - Active, 0 - Inactive))
  * newsletter (0 - no, 1 - yes)
* teams
  * team_id
  * program_name
  * program_number
  * team_name
  * start_date (python datetime object)
  * active (1 - Active, 0 - Inactive)
  * members (list under this)
    * barcode
    * type (0 = student, 1 = mentor, 2 = coach, -1 = other)
* customReports
  * report_id
  * name
  * sql_text
* certifications
  * barcode (who is being certified)
  * tool_id (1-18, look at certifications.py for mapping)
  * level (0 = NONE, 1 = BASIC, 10 = CERTIFIED, 20 = DOF, 30 = INSTRUCTOR, 40 = CERTIFIER)
  * date (python datetime ojbect)
  * certifier (barcode of certifier)
* accounts
  * user
  * password (before salting and hashing)        
  * barcode
  * role (bitwise combination of 0x04: COACH, 0x08: SHOP_CERTIFIER, 0x10: KEYHOLDER, 0x20: ADMIN, 0x40: SHOP_STEWARD)
* devices
  * mac
  * name
  * barcode
* unlocks
  * time (python datetime object)
  * location (text string)
  * barcode
* config
  * key
  * value

