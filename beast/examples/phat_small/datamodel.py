""" Data Model interface v2.0
BEAST datamodel for the example based on M31 PHAT data
"""

import numpy as np

# BEAST imports
from beast.physicsmodel.stars import isochrone
from beast.physicsmodel.stars import stellib
from beast.physicsmodel.dust import extinction
from beast.observationmodel.observations import Observations
from beast.observationmodel.vega import Vega
from beast.observationmodel.noisemodel import absflux_covmat
from beast.external.ezunits import unit
#from extra_filters import make_integration_filter, make_top_hat_filter

#-----------------------------------------------------------------
# User inputs                                   [sec:conf]
#-----------------------------------------------------------------
# Parameters that are required to make models
# and to fit the data
#-----------------------------------------------------------------
# AC == authomatically created
# indicates where user's input change is NOT necessary/recommeded
#-----------------------------------------------------------------

# project : string
#   the name of the output results directory
project = 'beast_example_phat'

# filters : list of strings
#   full filter names in BEAST filter database
filters = ['HST_WFC3_F275W','HST_WFC3_F336W','HST_ACS_WFC_F475W',
           'HST_ACS_WFC_F814W', 'HST_WFC3_F110W','HST_WFC3_F160W']

# basefilters : list of strings
#   short names for filters
basefilters = ['F275W','F336W','F475W',
               'F814W','F110W','F160W']

# obs_colnames : list of strings
#   names of columns for filters in the observed catalog
#   need to match column names in the observed catalog,
#   input data MUST be in fluxes, NOT in magnitudes 
#   fluxes MUST be in normalized Vega units
obs_colnames = [ f.lower() + '_rate' for f in basefilters ]

# obsfile : string 
#   pathname of the observed catalog
obsfile = 'data/b15_4band_det_27_A.fits'

#------------------------------------------------------
# Artificial Star Test Input File Generation Parameters
#------------------------------------------------------

# ast_models_selected_per_age : integer
# Number of models to pick per age (Default = 70).
ast_models_selected_per_age = 70  

# ast_bands_above_maglimit : integer 
# Number of filters that must be above the magnitude limit
# for an AST to be included in the list (Default = 3)
ast_bands_above_maglimit = 3  
                             

# ast_realization_per_model : integer
# Number of Realizations of each included AST model
# to be put into the list. (Default = 20)
ast_realization_per_model = 20
                             

# ast_maglimit : float (single value or array with one value per filter)
# (1) option 1: [number] to change the number of mags fainter than
#                  the 90th percentile
#               faintest star in the photometry catalog to be used for
#                  the mag cut.
#               (Default = 1)
# (2) option 2: [space-separated list of numbers] to set custom faint end limits
#               (one value for each band).
ast_maglimit = [1.] 

# ast_with_positions :  (bool,optional)
# If True, the ast list is produced with X,Y positions.
# If False, the ast list is produced with only magnitudes.
ast_with_positions = True
                         
# ast_pixel_distribution : float (optional)
# (Used if ast_with_positions is True), minimum pixel separation between AST
# position and catalog star used to determine the AST spatial distribution
ast_pixel_distribution = 10.0 

# ast_reference_image : string (optional, but required if ast_with_positions
# is True and no X and Y information  is present in the photometry catalog)	
# Name of the reference image used by DOLPHOT when running the measured 
# photometry.	            
ast_reference_image = None


#-------------------------------------------
#Noise Model Artificial Star Test Parameters
#-------------------------------------------

# astfile : string
#   pathname of the AST files (single camera ASTs)
astfile = 'data/fake_stars_b15_27_all.hd5'

# ast_colnames : list of strings 
#   names of columns for filters in the AST catalog (AC)
ast_colnames = np.array(basefilters)

# noisefile : string
#   create a name for the noise model
noisefile = project + '/' + project + '_noisemodel.hd5'

# absflux calibration covariance matrix for HST specific filters (AC)
absflux_a_matrix = absflux_covmat.hst_frac_matrix(filters)

# distance modulus to the galaxy
distanceModulus = 24.47 * unit['mag']

################

### Stellar grid definition

# log10(Age) -- [min,max,step] to generate the isochrones in years
#   example [6.0, 10.13, 1.0]
logt = [6.0, 10.13, 1.0]

# note: Mass is not sampled, instead the isochrone supplied
#       mass spacing is used instead

# Metallicity : list of floats
#   Here: Z == Z_initial, NOT Z(t) surface abundance
#   PARSECv1.2S accepts values 1.e-4 < Z < 0.06
#   example z = [0.03, 0.019, 0.008, 0.004]
#   can they be set as [min, max, step]?
z = [0.03, 0.019, 0.008, 0.004]

# Isochrone Model Grid
#   Current Choices: Padova or MIST
#   PadovaWeb() -- `modeltype` param for iso sets from ezpadova
#      (choices: parsec12s_r14, parsec12s, 2010, 2008, 2002)
#   MISTWeb() -- `rotation` param (choices: vvcrit0.0=default, vvcrit0.4)
#
# Default: PARSEC+CALIBRI
oiso = isochrone.PadovaWeb()
# Alternative: PARSEC1.2S -- old grid parameters
#oiso = isochrone.PadovaWeb(modeltype='parsec12s', filterPMS=True)
# Alternative: MIST -- v1, no rotation
#oiso = isochrone.MISTWeb()

# Stellar Atmospheres library definition
osl = stellib.Tlusty() + stellib.Kurucz()

################

### Dust extinction grid definition
extLaw = extinction.Gordon16_RvFALaw()

# A(V): dust column in magnitudes
#   acceptable avs > 0.0
#   example [min, max, step] = [0.0, 10.055, 1.0]
avs = [0.0, 10.055, 1.0]

# R(V): dust average grain size
#   example [min, max, step] = [2.0,6.0,1.0]
rvs = [2.0,6.0,1.0]

# fA: mixture factor between "MW" and "SMCBar" extinction curves
#   example [min, max, step] = [0.0,1.0, 0.25]
fAs = [0.0,1.0, 0.25]

################

# add in the standard filters to enable output of stats and pdf1d values
# for the observed fitlers (AC)
add_spectral_properties_kwargs = dict(filternames=filters)

################
# The following code does not require user's attention (AC)
################

class GenFluxCatalog(Observations):
    """Generic n band filter photometry
    This class implements a direct access to the Generic HST measured fluxes.

    ..note::
        it does not implement uncertainties as in this model, the noise is
        given through artificial star tests
    """
    def __init__(self, inputFile, distanceModulus=distanceModulus,
                 filters=filters):
        """ Construct the interface """
        desc = 'GENERIC star: %s' % inputFile
        Observations.__init__(self, inputFile, distanceModulus, desc=desc)
        self.setFilters( filters )
        #some bad values smaller than expected
        # in physical flux units
        self.setBadValue(6e-40)

        # rate column needed as this is the *flux* column
        for ik,k in enumerate(filters):
            self.data.set_alias(k, obs_colnames[ik])

    def getFlux(self, num, units=False):
        """returns the absolute flux of an observation 

        Parameters
        ----------
        num: int
            index of the star in the catalog to get measurement from

        units: bool
            if set returns the fluxes with a unit capsule

        Returns
        -------
        flux: ndarray[dtype=float, ndim=1]
            Measured integrated flux values throughout the filters 
            in erg/s/cm^2/A
        """

        # case for using '_flux' result
        d = self.data[num]
        
        flux = np.array([ d[self.data.resolve_alias(ok)] 
                          for ok in self.filters ]) * self.vega_flux
        
        if units is True:
            return flux * unit['erg/s/cm**2/Angstrom']
        else:
            return flux

    def setFilters(self, filters):
        """ set the filters and update the vega reference for the conversions

        Parameters
        ----------
        filters: sequence
            list of filters using the internally normalized namings
        """
        self.filters = filters

        #Data "rates" are normalized to Vega already, fits are not using vega

        # for optimization purpose: pre-compute
        #   getting vega mags, require to open and read the content of one file.
        #   since getObs, calls getFlux, for each star you need to do this
        #   expensive operation
        with Vega() as v:
            _, vega_flux, _ = v.getFlux(filters)

        self.vega_flux = vega_flux


def get_obscat(obsfile=obsfile, distanceModulus=distanceModulus,
               filters=filters, *args, **kwargs):
    """ Function that generates a data catalog object with the correct
    arguments

    Parameters
    ----------
    obsfile: str, optional (default datamodel.obsfile)
        observation file

    distanceModulus: float, optional (default datamodel.distanceModulus)
        distance modulus to correct the data from (in magitude)

    filters: sequence(str), optional, datamodel.filters
        seaquence of filters of the data

    returns
    -------
    obs: GenFluxCatalog
        observation catalog
    """
    obs = GenFluxCatalog(obsfile, distanceModulus=distanceModulus,
                         filters=filters)
    return obs
