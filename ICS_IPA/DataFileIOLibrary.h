#pragma once

#if defined(PYD) && defined(_WIN32)
#define EXPORT_SPEC __declspec(dllexport)
#elif defined(_WINDLL)
#define EXPORT_SPEC __declspec(dllexport) __stdcall
#else
#define EXPORT_SPEC 
#endif

typedef double * DATA_PTR;

extern "C" 
{
/** @brief Returns the number of channels read from the
 *  JSON file.
 *
 *  @param  pJsonFile The full path to the JSON file to read
 *  @return The number of channels read
 */
int EXPORT_SPEC GetNumChannels(const char *pJsonFile);

/** @brief Opens a data file, reads the potential channel names to process
 *  from the JSON file and writes out a JSON containing the exact 
 *  channels found.  This list can then be used in the OpenDataFile call.
 *
 *  If the number of channels found is less than all the channels
 *  of interest, this call returns 0.
 *
 *  If an error occurred, on windows, a debug message is emitted 
 *  describing the problem.
 *
 *  Timestamps used throughout represent the number of seconds since
 *  start of measurement.  The decimals represent fractions of seconds.
 *
 *  @param pDataFile     The full path to the DB/MDF file to process
 *  @param pPrioritizedSignalJsonFile   The full path to the JSON file to read
 *  @param pValidSignalJsonFile         The full path to the output JSON file
 *  @return The number of channels found or, in case of error:
 *           0 if the number of data channels found does not match the number
               of channels in the JSON file
 *          -1 if the Data Spy license is invalid
 *          -2 if the Data file is invalid
 *          -3 if the JSON file is invalid
 */
int EXPORT_SPEC ValidateSignals(const char *pDataFile, const char *pPrioritizedSignalJsonFile, const char *pValidSignalJsonFile);

/** @brief Opens a DB file, reads the channels to process
 *  from the JSON file, allocates memory for the channel
 *  values and timestamps and returns the start of measurement
 *  time.
 *  
 *  If the number of channels found is less than all the channels
 *  of interest, this call returns 0.
 *
 *  If an error occurred, on windows, a debug message is emitted 
 *  describing the problem.
 *
 *  Timestamps used throughout represent the number of seconds since
 *  start of measurement.  The decimals represent fractions of seconds.
 *
 *  @param pDbFile     The full path to the DB file to process
 *  @param pJsonFile   The full path to the JSON file to read
 *  @param datapointer The allocated memory for the channel values
 *  @param timestamps  The allocated memory for the channel timestamps
 *  @param n           The size for the channel values and timestamps
 *  @return The start of Measurement timestamp or in case of error:
 *           0 if the number of data channels found does not match the number
               of channels in the JSON file
 *          -1 if the Data Spy license is invalid
 *          -2 if the Data file is invalid
 *          -3 if the JSON file is invalid
 */
double EXPORT_SPEC OpenDataFile(const char *pDbFile, const char *pJsonFile, double ** datapointer, double ** timestamps, int * n);

/** @brief Allows the user to use only a subset of the channels to
 *  determine the next time value.
 *  
 *  If an error ocurred, the return value is 0.
 *
 *  @param indatapointer The datapointer value received from the OpenDataFile call
 *  @param n             The number of channels (size of the datapointer array)
 *  @param pMask         A string of size n containing the character '1' for active
 *                       channels and '0' for non-active channels.  Please note that
 *                       only '0' and '1' are valid values.
 *  @return 1 for success, 0 for error
 */
int EXPORT_SPEC SetActiveMask(double * indatapointer, int n, const char *pMask);

/** @brief Allows the user to position the time cursor just before or at the specified
 *  time value.  This call updates the channel values and timestamps.  If only some 
 *  channels are active, the nearest active channel's timestamp is used.
 *  
 *  If an error ocurred, the return value is DBL_MAX
 *
 *  Timestamps represent the number of seconds since start of measurement.  The decimals 
 *  represent fractions of seconds.
 *
 *  @param indatapointer The datapointer value received from the OpenDataFile call
 *  @param n             The number of channels (size of the datapointer array)
 *  @param dTime         The timestamp to jump to
 *  @return The actual timestamp the cursor is on
 */
double EXPORT_SPEC JumpBeforeTimestamp(double * indatapointer, int n, double dTime);

/** @brief Allows the user to position the time cursor just after or at the specified
 *  time value.  This call updates the channel values and timestamps.  The first
 *  timestamp where all channels have a value and which is at or after the requested
 *  time.  If only some channels are active, the nearest active channel's timestamp is
 *  used.
 *  
 *  If an error ocurred, the return value is DBL_MAX
 *
 *  Timestamps represent the number of seconds since start of measurement.  The decimals 
 *  represent fractions of seconds.
 *
 *  @param indatapointer The datapointer value received from the OpenDataFile call
 *  @param n             The number of channels (size of the datapointer array)
 *  @param dTime         The timestamp to jump to
 *  @return The actual timestamp the cursor is on
 */
double EXPORT_SPEC JumpAfterTimestamp(double * indatapointer, int n, double dTime);

/** @brief Advances the cursor to the next timestamp.  This call updates the channel
 *  values and timestamps.  If only some channels are active, the next timestamp of
 *  an active channel is the one returned.
 *  
 *  If an error ocurred, the return value is DBL_MAX
 *
 *  @param indatapointer The datapointer value received from the OpenDataFile call
 *  @param n             The number of channels (size of the datapointer array)
 *  @return The actual timestamp the cursor is on
 */
double EXPORT_SPEC GetNextRecord(double * indatapointer, int n);

/** @brief Advances the cursor to the next record with changed signal values.
 *  This call updates the channel values and timestamps.  If only some channels are 
 *  active, the next timestamp of an active channel is the one returned.
 *  
 *  If an error ocurred, the return value is DBL_MAX
 *
 *  @param indatapointer The datapointer value received from the OpenDataFile call
 *  @param n             The number of channels (size of the datapointer array)
 *  @return The actual timestamp the cursor is on
 */
double EXPORT_SPEC GetNextChangedRecord(double * indatapointer, int n);

/** @brief Advances the cursor to the next record with valid signal values.  An 
 *  invalid signal contains DBL_MAX as the value.  This call updates the channel 
 *  values and timestamps.  If only some channels are active, the next timestamp 
 *  of an active channel is the one returned.
 *  
 *  If an error ocurred, the return value is DBL_MAX
 *
 *  @param indatapointer The datapointer value received from the OpenDataFile call
 *  @param n             The number of channels (size of the datapointer array)
 *  @return The actual timestamp the cursor is on
 */
double EXPORT_SPEC GetNextValidRecord(double * indatapointer, int n);

/** @brief Sets the cursor to the first timestamp for each channel.  This call updates 
 *  the channel values and timestamps.
 *  
 *  If an error ocurred, the return value is DBL_MAX
 *
 *  @param indatapointer The datapointer value received from the OpenDataFile call
 *  @param n             The number of channels (size of the datapointer array)
 *  @return The actual timestamp the cursor is on
 */
double EXPORT_SPEC SetCursorsToStart(double * indatapointer, int n);

/** @brief Returns the start and end or measurement times found in the file.
 *  
 *  If an error ocurred, the return value is 0.
 *
 *  Timestamps used throughout represent the number of seconds since
 *  January 1, 2007.  The decimals represent fractions of seconds.
 *
 *  @param indatapointer The datapointer value received from the OpenDataFile call
 *  @param n             The number of channels (size of the datapointer array)
 *  @param pMask         A string of size n containing the character '1' for active
 *                       channels and '0' for non-active channels.  Please note that
 *                       only '0' and '1' are valid values.
 *  @return 1 for success, 0 for error
 */
int EXPORT_SPEC GetMeasurementTimeBounds(double * indatapointer, int n, double *startTime, double *endTime);

/** @brief Closes the file and frees memory
 *  
 *  If an error ocurred, the return value is 0.
 *
 *  @param indatapointer The datapointer value received from the OpenDataFile call
 *  @param n             The number of channels (size of the datapointer array)
 *  @return 1 for success, 0 for error
 */
int EXPORT_SPEC CloseDataFile(double * indatapointer, int n);

/** @brief Creates a DB file using the data found in the specified MDF file.
 *  
 *  If the Data Spy license is invalid, this call returns -1
 *  
 *  If an error ocurred, the return value is 0.  In addition, on
 *  windows, a debug message is emitted describing the problem.
 *
 *  @param pMdfFile    The full path to the MDF file to read
 *  @param pDbFile     The full path to the DB file to write
 *  @return 1 for success, 0 for error, -1 for licensing issues
 */
int EXPORT_SPEC CreateDatabase(const char *pMdfFile, const char *pDbFile);

/** @brief Creates a DB file using the data found in the specified MDF file.
 *  Only the channels specified in the JSON file are written.
 *  
 *  If the Data Spy license is invalid, this call returns -1
 *  
 *  If an error ocurred, the return value is 0.  In addition, on
 *  windows, a debug message is emitted describing the problem.
 *
 *  @param pMdfFile    The full path to the MDF file to read
 *  @param pJsonFile   The full path to the JSON file to read
 *  @param pDbFile     The full path to the DB file to write
 *  @return 1 for success, 0 for error, -1 for licensing issues
 */
int EXPORT_SPEC CreateDatabaseForSignals(const char *pMdfFile, const char *pJsonFile, const char *pDbFile);

/** @brief Creates a JSON file containing the channels found in the 
 *  specified MDF file.  MDF 3.x and 4.x files are supported seamlessly.
 *  
 *  If an error ocurred, the return value is 0.
 *
 *  @param pMdfFile    The full path to the MDF file to read
 *  @param pJsonFile   The full path to the JSON file to write
 *  @return 1 for success, 0 for error, -1 for licensing issues
 */
int EXPORT_SPEC GetChannels(const char *pMdfFile, const char *pJsonFile);

/** @brief Creates a JSON file containing the various statistics (min/max/avg, etc)
 *  computed on the channels found in the specified MDF file.  MDF 3.x and 4.x files 
 *  are supported seamlessly.
 *  
 *  If an error ocurred, the return value is 0.
 *
 *  @param pMdfFile    The full path to the MDF file to read
 *  @param pJsonFile   The full path to the JSON file to write
 *  @return 1 for success, 0 for error, -1 for licensing issues
 */
int EXPORT_SPEC GetChannelStatistics(const char *pMdfFile, const char *pJsonFile);

/** @brief Creates an MDF file containing the selected channels found in the DB file specified.
 *  
 *  If the Data Spy license is invalid, this call returns -1
 *  
 *  If an error ocurred, the return value is 0.
 *
 *  @param pDbFile     The full path to the DB file to read
 *  @param pMdfFile    The full path to the MDF file to write
 *  @return 1 for success, 0 for error, -1 for licensing issues
 */
int EXPORT_SPEC ExportToMdf(const char *pDbFile, const char *pMdfFile);

/** @brief Creates an MDF file containing the selected channels found in the DB file specified
 *  using the force rate parameter specified.  Rates less than or equal to 0 will be treated
 *  as a regular data export.
 *  
 *  If the Data Spy license is invalid, this call returns -1
 *  
 *  If an error ocurred, the return value is 0.
 *
 *  @param pDbFile     The full path to the DB file to read
 *  @param pMdfFile    The full path to the MDF file to write
 *  @param dForceRate  The rate in seconds.  Use decimal values to specifies fractions.
 *  @return 1 for success, 0 for error, -1 for licensing issues
 */
int EXPORT_SPEC ExportToMdfForceRate(const char *pDbFile, const char *pMdfFile, double dForceRate);

/** @brief Creates an MDF or DB file containing the data specified in the dsr file
 *  
 *  If the Data Spy license is invalid, this call returns -1
 *  if the JSON file is invalid, this call returns -3
 *
 *  @param pScriptFile     The full path to the DSR file to read
 *  @param pOutFile    The full path to the MDF/DB file to write
 *  @return 0 for success, -1 for licensing issues, -3 is the DSR file is invalid
 */
int EXPORT_SPEC OutputHitsToFile(const char *pScriptFile, const char *pOutFile);

/** @brief The following functions take Unicode paths which are needed
 *  for various extended character versions of Windows.  They function the same
 *  the functions described above do.
 */

int EXPORT_SPEC GetNumChannelsW(const wchar_t *pJsonFile);
int EXPORT_SPEC ValidateSignalsW(const wchar_t *pDbFile, const wchar_t *pPrioritizedSignalJsonFile, const wchar_t *pValidSignalJsonFile);
double EXPORT_SPEC OpenDataFileW(const wchar_t *pFile, const wchar_t *pJsonFile, double ** datapointer, double ** timestamps, int * n);
int EXPORT_SPEC CreateDatabaseW(const wchar_t *pMdfFile, const wchar_t *pDbFile);
int EXPORT_SPEC CreateDatabaseForSignalsW(const wchar_t *pMdfFile, const wchar_t *pJsonFile, const wchar_t *pDbFile);
int EXPORT_SPEC GetChannelsW(const wchar_t *pMdfFile, const wchar_t *pJsonFile);
int EXPORT_SPEC GetChannelStatisticsW(const wchar_t *pMdfFile, const wchar_t *pJsonFile);
int EXPORT_SPEC ExportToMdfW(const wchar_t *pDbFile, const wchar_t *pMdfFile);
int EXPORT_SPEC ExportToMdfForceRateW(const wchar_t *pDbFile, const wchar_t *pMdfFile, double dForceRate);
int EXPORT_SPEC OutputHitsToFileW(const wchar_t *pScriptFile, const wchar_t *pOutFile);
}