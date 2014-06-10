#
# Generated Makefile - do not edit!
#
# Edit the Makefile in the project folder instead (../Makefile). Each target
# has a -pre and a -post target defined where you can add customized code.
#
# This makefile implements configuration specific macros and targets.


# Include project Makefile
ifeq "${IGNORE_LOCAL}" "TRUE"
# do not include local makefile. User is passing all local related variables already
else
include Makefile
# Include makefile containing local settings
ifeq "$(wildcard nbproject/Makefile-local-default.mk)" "nbproject/Makefile-local-default.mk"
include nbproject/Makefile-local-default.mk
endif
endif

# Environment
MKDIR=mkdir -p
RM=rm -f 
MV=mv 
CP=cp 

# Macros
CND_CONF=default
ifeq ($(TYPE_IMAGE), DEBUG_RUN)
IMAGE_TYPE=debug
OUTPUT_SUFFIX=cof
DEBUGGABLE_SUFFIX=cof
FINAL_IMAGE=dist/${CND_CONF}/${IMAGE_TYPE}/QuizShow.X.${IMAGE_TYPE}.${OUTPUT_SUFFIX}
else
IMAGE_TYPE=production
OUTPUT_SUFFIX=hex
DEBUGGABLE_SUFFIX=cof
FINAL_IMAGE=dist/${CND_CONF}/${IMAGE_TYPE}/QuizShow.X.${IMAGE_TYPE}.${OUTPUT_SUFFIX}
endif

# Object Directory
OBJECTDIR=build/${CND_CONF}/${IMAGE_TYPE}

# Distribution Directory
DISTDIR=dist/${CND_CONF}/${IMAGE_TYPE}

# Source Files Quoted if spaced
SOURCEFILES_QUOTED_IF_SPACED=../lumos_init.asm ../lumos_main.asm ../serial-io.asm ../quizshow_init.asm ../quizshow_main.asm

# Object Files Quoted if spaced
OBJECTFILES_QUOTED_IF_SPACED=${OBJECTDIR}/_ext/1472/lumos_init.o ${OBJECTDIR}/_ext/1472/lumos_main.o ${OBJECTDIR}/_ext/1472/serial-io.o ${OBJECTDIR}/_ext/1472/quizshow_init.o ${OBJECTDIR}/_ext/1472/quizshow_main.o
POSSIBLE_DEPFILES=${OBJECTDIR}/_ext/1472/lumos_init.o.d ${OBJECTDIR}/_ext/1472/lumos_main.o.d ${OBJECTDIR}/_ext/1472/serial-io.o.d ${OBJECTDIR}/_ext/1472/quizshow_init.o.d ${OBJECTDIR}/_ext/1472/quizshow_main.o.d

# Object Files
OBJECTFILES=${OBJECTDIR}/_ext/1472/lumos_init.o ${OBJECTDIR}/_ext/1472/lumos_main.o ${OBJECTDIR}/_ext/1472/serial-io.o ${OBJECTDIR}/_ext/1472/quizshow_init.o ${OBJECTDIR}/_ext/1472/quizshow_main.o

# Source Files
SOURCEFILES=../lumos_init.asm ../lumos_main.asm ../serial-io.asm ../quizshow_init.asm ../quizshow_main.asm


CFLAGS=
ASFLAGS=
LDLIBSOPTIONS=

############# Tool locations ##########################################
# If you copy a project from one host to another, the path where the  #
# compiler is installed may be different.                             #
# If you open this project with MPLAB X in the new host, this         #
# makefile will be regenerated and the paths will be corrected.       #
#######################################################################
# fixDeps replaces a bunch of sed/cat/printf statements that slow down the build
FIXDEPS=fixDeps

.build-conf:  ${BUILD_SUBPROJECTS}
	${MAKE}  -f nbproject/Makefile-default.mk dist/${CND_CONF}/${IMAGE_TYPE}/QuizShow.X.${IMAGE_TYPE}.${OUTPUT_SUFFIX}

MP_PROCESSOR_OPTION=18f4685
MP_LINKER_DEBUG_OPTION= -u_DEBUGCODESTART=0x17dc0 -u_DEBUGCODELEN=0x240 -u_DEBUGDATASTART=0xcf4 -u_DEBUGDATALEN=0xb
# ------------------------------------------------------------------------------------
# Rules for buildStep: assemble
ifeq ($(TYPE_IMAGE), DEBUG_RUN)
${OBJECTDIR}/_ext/1472/lumos_init.o: ../lumos_init.asm  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1472 
	@${RM} ${OBJECTDIR}/_ext/1472/lumos_init.o.d 
	@${RM} ${OBJECTDIR}/_ext/1472/lumos_init.o 
	@${FIXDEPS} dummy.d -e "${OBJECTDIR}/_ext/1472/lumos_init.err" $(SILENT) -c ${MP_AS} $(MP_EXTRA_AS_PRE) -d__DEBUG -d__MPLAB_DEBUGGER_PICKIT2=1 -q -p$(MP_PROCESSOR_OPTION) -u  -l\\\"${OBJECTDIR}/_ext/1472/lumos_init.lst\\\" -e\\\"${OBJECTDIR}/_ext/1472/lumos_init.err\\\" $(ASM_OPTIONS)   -o\\\"${OBJECTDIR}/_ext/1472/lumos_init.o\\\" \\\"../lumos_init.asm\\\" 
	@${DEP_GEN} -d "${OBJECTDIR}/_ext/1472/lumos_init.o"
	@${FIXDEPS} "${OBJECTDIR}/_ext/1472/lumos_init.o.d" $(SILENT) -rsi ${MP_AS_DIR} -c18 
	
${OBJECTDIR}/_ext/1472/lumos_main.o: ../lumos_main.asm  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1472 
	@${RM} ${OBJECTDIR}/_ext/1472/lumos_main.o.d 
	@${RM} ${OBJECTDIR}/_ext/1472/lumos_main.o 
	@${FIXDEPS} dummy.d -e "${OBJECTDIR}/_ext/1472/lumos_main.err" $(SILENT) -c ${MP_AS} $(MP_EXTRA_AS_PRE) -d__DEBUG -d__MPLAB_DEBUGGER_PICKIT2=1 -q -p$(MP_PROCESSOR_OPTION) -u  -l\\\"${OBJECTDIR}/_ext/1472/lumos_main.lst\\\" -e\\\"${OBJECTDIR}/_ext/1472/lumos_main.err\\\" $(ASM_OPTIONS)   -o\\\"${OBJECTDIR}/_ext/1472/lumos_main.o\\\" \\\"../lumos_main.asm\\\" 
	@${DEP_GEN} -d "${OBJECTDIR}/_ext/1472/lumos_main.o"
	@${FIXDEPS} "${OBJECTDIR}/_ext/1472/lumos_main.o.d" $(SILENT) -rsi ${MP_AS_DIR} -c18 
	
${OBJECTDIR}/_ext/1472/serial-io.o: ../serial-io.asm  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1472 
	@${RM} ${OBJECTDIR}/_ext/1472/serial-io.o.d 
	@${RM} ${OBJECTDIR}/_ext/1472/serial-io.o 
	@${FIXDEPS} dummy.d -e "${OBJECTDIR}/_ext/1472/serial-io.err" $(SILENT) -c ${MP_AS} $(MP_EXTRA_AS_PRE) -d__DEBUG -d__MPLAB_DEBUGGER_PICKIT2=1 -q -p$(MP_PROCESSOR_OPTION) -u  -l\\\"${OBJECTDIR}/_ext/1472/serial-io.lst\\\" -e\\\"${OBJECTDIR}/_ext/1472/serial-io.err\\\" $(ASM_OPTIONS)   -o\\\"${OBJECTDIR}/_ext/1472/serial-io.o\\\" \\\"../serial-io.asm\\\" 
	@${DEP_GEN} -d "${OBJECTDIR}/_ext/1472/serial-io.o"
	@${FIXDEPS} "${OBJECTDIR}/_ext/1472/serial-io.o.d" $(SILENT) -rsi ${MP_AS_DIR} -c18 
	
${OBJECTDIR}/_ext/1472/quizshow_init.o: ../quizshow_init.asm  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1472 
	@${RM} ${OBJECTDIR}/_ext/1472/quizshow_init.o.d 
	@${RM} ${OBJECTDIR}/_ext/1472/quizshow_init.o 
	@${FIXDEPS} dummy.d -e "${OBJECTDIR}/_ext/1472/quizshow_init.err" $(SILENT) -c ${MP_AS} $(MP_EXTRA_AS_PRE) -d__DEBUG -d__MPLAB_DEBUGGER_PICKIT2=1 -q -p$(MP_PROCESSOR_OPTION) -u  -l\\\"${OBJECTDIR}/_ext/1472/quizshow_init.lst\\\" -e\\\"${OBJECTDIR}/_ext/1472/quizshow_init.err\\\" $(ASM_OPTIONS)   -o\\\"${OBJECTDIR}/_ext/1472/quizshow_init.o\\\" \\\"../quizshow_init.asm\\\" 
	@${DEP_GEN} -d "${OBJECTDIR}/_ext/1472/quizshow_init.o"
	@${FIXDEPS} "${OBJECTDIR}/_ext/1472/quizshow_init.o.d" $(SILENT) -rsi ${MP_AS_DIR} -c18 
	
${OBJECTDIR}/_ext/1472/quizshow_main.o: ../quizshow_main.asm  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1472 
	@${RM} ${OBJECTDIR}/_ext/1472/quizshow_main.o.d 
	@${RM} ${OBJECTDIR}/_ext/1472/quizshow_main.o 
	@${FIXDEPS} dummy.d -e "${OBJECTDIR}/_ext/1472/quizshow_main.err" $(SILENT) -c ${MP_AS} $(MP_EXTRA_AS_PRE) -d__DEBUG -d__MPLAB_DEBUGGER_PICKIT2=1 -q -p$(MP_PROCESSOR_OPTION) -u  -l\\\"${OBJECTDIR}/_ext/1472/quizshow_main.lst\\\" -e\\\"${OBJECTDIR}/_ext/1472/quizshow_main.err\\\" $(ASM_OPTIONS)   -o\\\"${OBJECTDIR}/_ext/1472/quizshow_main.o\\\" \\\"../quizshow_main.asm\\\" 
	@${DEP_GEN} -d "${OBJECTDIR}/_ext/1472/quizshow_main.o"
	@${FIXDEPS} "${OBJECTDIR}/_ext/1472/quizshow_main.o.d" $(SILENT) -rsi ${MP_AS_DIR} -c18 
	
else
${OBJECTDIR}/_ext/1472/lumos_init.o: ../lumos_init.asm  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1472 
	@${RM} ${OBJECTDIR}/_ext/1472/lumos_init.o.d 
	@${RM} ${OBJECTDIR}/_ext/1472/lumos_init.o 
	@${FIXDEPS} dummy.d -e "${OBJECTDIR}/_ext/1472/lumos_init.err" $(SILENT) -c ${MP_AS} $(MP_EXTRA_AS_PRE) -q -p$(MP_PROCESSOR_OPTION) -u  -l\\\"${OBJECTDIR}/_ext/1472/lumos_init.lst\\\" -e\\\"${OBJECTDIR}/_ext/1472/lumos_init.err\\\" $(ASM_OPTIONS)   -o\\\"${OBJECTDIR}/_ext/1472/lumos_init.o\\\" \\\"../lumos_init.asm\\\" 
	@${DEP_GEN} -d "${OBJECTDIR}/_ext/1472/lumos_init.o"
	@${FIXDEPS} "${OBJECTDIR}/_ext/1472/lumos_init.o.d" $(SILENT) -rsi ${MP_AS_DIR} -c18 
	
${OBJECTDIR}/_ext/1472/lumos_main.o: ../lumos_main.asm  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1472 
	@${RM} ${OBJECTDIR}/_ext/1472/lumos_main.o.d 
	@${RM} ${OBJECTDIR}/_ext/1472/lumos_main.o 
	@${FIXDEPS} dummy.d -e "${OBJECTDIR}/_ext/1472/lumos_main.err" $(SILENT) -c ${MP_AS} $(MP_EXTRA_AS_PRE) -q -p$(MP_PROCESSOR_OPTION) -u  -l\\\"${OBJECTDIR}/_ext/1472/lumos_main.lst\\\" -e\\\"${OBJECTDIR}/_ext/1472/lumos_main.err\\\" $(ASM_OPTIONS)   -o\\\"${OBJECTDIR}/_ext/1472/lumos_main.o\\\" \\\"../lumos_main.asm\\\" 
	@${DEP_GEN} -d "${OBJECTDIR}/_ext/1472/lumos_main.o"
	@${FIXDEPS} "${OBJECTDIR}/_ext/1472/lumos_main.o.d" $(SILENT) -rsi ${MP_AS_DIR} -c18 
	
${OBJECTDIR}/_ext/1472/serial-io.o: ../serial-io.asm  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1472 
	@${RM} ${OBJECTDIR}/_ext/1472/serial-io.o.d 
	@${RM} ${OBJECTDIR}/_ext/1472/serial-io.o 
	@${FIXDEPS} dummy.d -e "${OBJECTDIR}/_ext/1472/serial-io.err" $(SILENT) -c ${MP_AS} $(MP_EXTRA_AS_PRE) -q -p$(MP_PROCESSOR_OPTION) -u  -l\\\"${OBJECTDIR}/_ext/1472/serial-io.lst\\\" -e\\\"${OBJECTDIR}/_ext/1472/serial-io.err\\\" $(ASM_OPTIONS)   -o\\\"${OBJECTDIR}/_ext/1472/serial-io.o\\\" \\\"../serial-io.asm\\\" 
	@${DEP_GEN} -d "${OBJECTDIR}/_ext/1472/serial-io.o"
	@${FIXDEPS} "${OBJECTDIR}/_ext/1472/serial-io.o.d" $(SILENT) -rsi ${MP_AS_DIR} -c18 
	
${OBJECTDIR}/_ext/1472/quizshow_init.o: ../quizshow_init.asm  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1472 
	@${RM} ${OBJECTDIR}/_ext/1472/quizshow_init.o.d 
	@${RM} ${OBJECTDIR}/_ext/1472/quizshow_init.o 
	@${FIXDEPS} dummy.d -e "${OBJECTDIR}/_ext/1472/quizshow_init.err" $(SILENT) -c ${MP_AS} $(MP_EXTRA_AS_PRE) -q -p$(MP_PROCESSOR_OPTION) -u  -l\\\"${OBJECTDIR}/_ext/1472/quizshow_init.lst\\\" -e\\\"${OBJECTDIR}/_ext/1472/quizshow_init.err\\\" $(ASM_OPTIONS)   -o\\\"${OBJECTDIR}/_ext/1472/quizshow_init.o\\\" \\\"../quizshow_init.asm\\\" 
	@${DEP_GEN} -d "${OBJECTDIR}/_ext/1472/quizshow_init.o"
	@${FIXDEPS} "${OBJECTDIR}/_ext/1472/quizshow_init.o.d" $(SILENT) -rsi ${MP_AS_DIR} -c18 
	
${OBJECTDIR}/_ext/1472/quizshow_main.o: ../quizshow_main.asm  nbproject/Makefile-${CND_CONF}.mk
	@${MKDIR} ${OBJECTDIR}/_ext/1472 
	@${RM} ${OBJECTDIR}/_ext/1472/quizshow_main.o.d 
	@${RM} ${OBJECTDIR}/_ext/1472/quizshow_main.o 
	@${FIXDEPS} dummy.d -e "${OBJECTDIR}/_ext/1472/quizshow_main.err" $(SILENT) -c ${MP_AS} $(MP_EXTRA_AS_PRE) -q -p$(MP_PROCESSOR_OPTION) -u  -l\\\"${OBJECTDIR}/_ext/1472/quizshow_main.lst\\\" -e\\\"${OBJECTDIR}/_ext/1472/quizshow_main.err\\\" $(ASM_OPTIONS)   -o\\\"${OBJECTDIR}/_ext/1472/quizshow_main.o\\\" \\\"../quizshow_main.asm\\\" 
	@${DEP_GEN} -d "${OBJECTDIR}/_ext/1472/quizshow_main.o"
	@${FIXDEPS} "${OBJECTDIR}/_ext/1472/quizshow_main.o.d" $(SILENT) -rsi ${MP_AS_DIR} -c18 
	
endif

# ------------------------------------------------------------------------------------
# Rules for buildStep: link
ifeq ($(TYPE_IMAGE), DEBUG_RUN)
dist/${CND_CONF}/${IMAGE_TYPE}/QuizShow.X.${IMAGE_TYPE}.${OUTPUT_SUFFIX}: ${OBJECTFILES}  nbproject/Makefile-${CND_CONF}.mk    
	@${MKDIR} dist/${CND_CONF}/${IMAGE_TYPE} 
	${MP_LD} $(MP_EXTRA_LD_PRE)   -p$(MP_PROCESSOR_OPTION)  -w -x -u_DEBUG -z__ICD2RAM=1 -m"${DISTDIR}/${PROJECTNAME}.${IMAGE_TYPE}.map"   -z__MPLAB_BUILD=1  -z__MPLAB_DEBUG=1 -z__MPLAB_DEBUGGER_PICKIT2=1 $(MP_LINKER_DEBUG_OPTION) -odist/${CND_CONF}/${IMAGE_TYPE}/QuizShow.X.${IMAGE_TYPE}.${OUTPUT_SUFFIX}  ${OBJECTFILES_QUOTED_IF_SPACED}     
else
dist/${CND_CONF}/${IMAGE_TYPE}/QuizShow.X.${IMAGE_TYPE}.${OUTPUT_SUFFIX}: ${OBJECTFILES}  nbproject/Makefile-${CND_CONF}.mk   
	@${MKDIR} dist/${CND_CONF}/${IMAGE_TYPE} 
	${MP_LD} $(MP_EXTRA_LD_PRE)   -p$(MP_PROCESSOR_OPTION)  -w  -m"${DISTDIR}/${PROJECTNAME}.${IMAGE_TYPE}.map"   -z__MPLAB_BUILD=1  -odist/${CND_CONF}/${IMAGE_TYPE}/QuizShow.X.${IMAGE_TYPE}.${DEBUGGABLE_SUFFIX}  ${OBJECTFILES_QUOTED_IF_SPACED}     
endif


# Subprojects
.build-subprojects:


# Subprojects
.clean-subprojects:

# Clean Targets
.clean-conf: ${CLEAN_SUBPROJECTS}
	${RM} -r build/default
	${RM} -r dist/default

# Enable dependency checking
.dep.inc: .depcheck-impl

DEPFILES=$(shell "${PATH_TO_IDE_BIN}"mplabwildcard ${POSSIBLE_DEPFILES})
ifneq (${DEPFILES},)
include ${DEPFILES}
endif
