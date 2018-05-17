# This file is no longer auto-generated to make the repository builds with GCC
# and ARMCC no matter what.

cmake_minimum_required(VERSION 2.8.12)

enable_language(ASM)

MACRO(RECURSIVE_FIND_FILE return_list dir pattern)
    FILE(GLOB_RECURSE new_list "${dir}/${pattern}")
    SET(dir_list "")
    FOREACH(file_path ${new_list})
        SET(dir_list ${dir_list} ${file_path})
    ENDFOREACH()
    LIST(REMOVE_DUPLICATES dir_list)
    SET(${return_list} ${dir_list})
ENDMACRO()

RECURSIVE_FIND_FILE(SOURCE_FILES "." "*.c??")

set(YOTTA_AUTO_SAMSUNG-RADIO_CPP_FILES
    ${SOURCE_FILES}
)

add_library(samsung-radio
    ${YOTTA_AUTO_SAMSUNG-RADIO_CPP_FILES}
)

yotta_postprocess_target(LIBRARY samsung-radio)

target_link_libraries(samsung-radio
    microbit-dal
)