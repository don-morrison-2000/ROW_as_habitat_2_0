
import row.constants as c
import row.registry
import row.adm.adm_utils
import row.adm.obj.organization
import traceback

import row.logger
logger = row.logger.get('row_log')


def run(gis, org_id,):
    logger.info ("Logging to %s" % row.logger.LOG_FILE)
    try:
        row.adm.obj.organization.delete(gis, org_id, False, False)
    except Exception as ex:
        logger.info (org_id + ': ' + str(ex))
        logger.debug (traceback.format_exc())
        logger.info ("%s: Deployment failed" % org_id)
    return


if __name__ == '__main__':
    logger.info ("Logging to %s" % row.logger.LOG_FILE)
    gis = row.adm.adm_utils.login_as_admin ()
    run(gis, 'ROW2_DEVOrgA')