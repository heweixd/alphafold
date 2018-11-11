from alphafold.explicit_recursions import *
import random

def get_random_contrib( contribs ):
    # Random sample weighted by probability. Must be a simple function for this.
    contrib_cumsum = [ contribs[0][0] ]
    for contrib in contribs[1:]: contrib_cumsum.append( contrib_cumsum[-1] + contrib[0] )
    r = random.random() * contrib_cumsum[ -1 ]
    for (idx,psum) in enumerate( contrib_cumsum ):
        if r < psum: return contribs[idx]

##################################################################################################
def backtrack( self, contribs_input, mode = 'mfe' ):
    if len( contribs_input ) == 0: return []
    contrib_sum = sum( contrib[0] for contrib in contribs_input )
    if   mode == 'enumerative': contribs = deepcopy( contribs_input )
    elif mode == 'mfe':         contribs = [ max( contribs_input ) ]
    elif mode == 'stochastic' : contribs = [ get_random_contrib( contribs_input ) ]
    p_bps = [] # list of tuples of (p_structure, bps_structure) for each structure
    N = self.N
    for contrib in contribs: # each option ('contribution' to this partition function of this sub-region)
        if ( contrib[0] == 0.0 ): continue
        p_contrib = contrib[0]/contrib_sum
        p_bps_contrib = [ [p_contrib,[]] ]

        for backtrack_info in contrib[1]: # each 'branch'
            ( Z_backtrack, i, j )  = backtrack_info
            if ( i == j ): continue
            if Z_backtrack == self.Z_BP:
                base_pair = [i%N,j%N]
                base_pair.sort()
                p_bps_contrib = [ [p_bp[0], p_bp[1]+[tuple( base_pair )] ] for p_bp in p_bps_contrib ]
            self.options.calc_contrib = True
            Z_backtrack.update( self, i, j )
            self.options.calc_contrib = False
            p_bps_component = backtrack( self, Z_backtrack.get_contribs(i%N,j%N), mode )
            if len( p_bps_component ) == 0: continue
            # put together all branches
            p_bps_contrib_new = []
            for p_bps1 in p_bps_contrib:
                for p_bps2 in p_bps_component:
                    p_bps_contrib_new.append( [p_bps1[0]*p_bps2[0], p_bps1[1]+p_bps2[1]] )
            p_bps_contrib = p_bps_contrib_new

        p_bps += p_bps_contrib
    return p_bps

##################################################################################################
def mfe( self, Z_final_contrib ):
    p_bps = backtrack( self, Z_final_contrib, mode = 'mfe' )
    assert( len(p_bps) == 1 )
    p,bps = p_bps[0]
    bps.sort()
    return (bps,p)

##################################################################################################
def boltzmann_sample( self, Z_final_contrib ):
    p_bps = backtrack( self, Z_final_contrib, mode = 'stochastic' )
    assert( len(p_bps) == 1 )
    return (p_bps[0][1],p_bps[0][0])

