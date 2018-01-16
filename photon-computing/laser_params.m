% sarah messing around with laser cutter parameters
% case: fixed time
clear;

t = 1; % seconds
dist = 0.05; % meters

h = 6.626068e-34;
focal_length = 0.07239; % meters = 2.85 inch flexx lens
mode = 1.2;
lambda = 1.06e-5; % meters
beam_diameter = 0.008; % meters (beam size before focusing)
spot_diameter =  (4 * lambda *focal_length * mode) / (pi * beam_diameter);
spot_size = (spot_diameter/2)^2 * pi; % meters squared

speed = 0.059:0.059:3.55; % m/s
power = 1.33:1.33:80; % watts
frequency = 1000:1000:60000; % Hz

photons_per_sec = power ./ (h * frequency);
photons_per_pulse = power / h;

photons_fixed_f = zeros(size(speed,2),size(power,2));
photons_fixed_p = zeros(size(speed,2),size(frequency,2));
photons_fixed_s = zeros(size(frequency,2),size(power,2));


i=1;
for s = speed
    j=1;
    for f = frequency
        between = s / f; % meters between each pulse
        if between < spot_diameter % over 25 percent speed
            photons_fixed_p(i,j) = (80 * f * t) / spot_size;
        else % under 25 percent speed
            area = spot_diameter * s * t; % meters squared, area covered by laser
            photons_fixed_p(i,j) = (80 * f * t) / area;
        end
        j = j+1;
    end
    i = i+1;
end


i=1;
for s = speed
    j=1;
    for p = photons_per_pulse
        between = s / 1000; % meters between each pulse
        if between < spot_diameter % over 25 percent speed
            photons_fixed_f(i,j) = (p * 2000 * t) / spot_size;
        else % under 25 percent speed
            area = spot_diameter * s * t; % meters squared, area covered by laser
            photons_fixed_f(i,j) = (p * 2000 * t) / area;
        end
        j = j+1;
    end
    i = i+1;
end


i=1;
for f = frequency
    j=1;
    between = 0.355 / f; % meters between each pulse
    for p = photons_per_pulse
        if between < spot_diameter % over 25 percent speed
            photons_fixed_s(i,j) = (p * f * t) / spot_size;
        else % under 25 percent speed
            area = spot_diameter * 0.355 * t; % meters squared, area covered by laser
            photons_fixed_s(i,j) = (p * f * t) / area;
            
        end
        j = j+1;
    end
    i = i+1;
end

speed_scatter = 0.1183:0.1183:3.55; % m/s
power_scatter = 2.66:2.66:80; % watts
frequency_scatter = 2000:2000:60000; % Hz

photons_per_sec = power_scatter ./ (h * frequency_scatter);
photons_per_pulse = power_scatter / h;

photons_per_area = zeros(size(speed_scatter,2),size(frequency_scatter,2),size(power_scatter,2));

i=1;
for s = speed_scatter
    j=1;
    for f = frequency_scatter
        between = s / f; % meters between each pulse
        k=1;
        for p = photons_per_pulse
            if between < spot_diameter % over 25 percent speed
                photons_per_area(i,j,k) = (p * f * t) / spot_size;
            else % under 25 percent speed
                area = spot_diameter * s * t; % meters squared, area covered by laser
                photons_per_area(i,j,k) = (p * f * t) / area;
            end
            k = k+1;
        end
        j = j+1;
    end
    i = i+1;
end

figure(1)
rotate3d on
colormap(flipud(hot))
xlim([0 3.55])
ylim([0 80])
[x,y] = meshgrid(speed,power);
z = photons_fixed_f;
m = surf(x,y, z','FaceLighting','gouraud','FaceColor','interp','LineWidth',0.00001);
m.CData = z';
title('Speed v Power: Photons per Square Meter')
xlabel('Speed (m/s)');
ylabel('Power (Watts)');
zlabel('# of Photons (n/m^2)');

figure(2)
rotate3d on
colormap(flipud(hot))
xlim([0 3.55])
ylim([0 60000])
[x,y] = meshgrid(speed,frequency);
z = photons_fixed_p;
m = surf(x,y, z','FaceLighting','gouraud','FaceColor','interp','LineWidth',0.001);
m.CData = z';
title('Speed v Frequency: Photons per Square Meter')
xlabel('Speed (m/s)');
ylabel('Frequency (Hz)');
zlabel('# of Photons (n/m^2)');

figure(3)
rotate3d on
colormap(flipud(hot))
xlim([0 60000])
ylim([0 80])
[x,y] = meshgrid(frequency,power);
z = photons_fixed_s;
m = surf(x,y, z','FaceLighting','gouraud','FaceColor','interp','LineWidth',0.001);
m.CData = z';
title('Frequency v Power: Photons per Square Meter')
xlabel('Frequency (Hz)');
ylabel('Power (Watts)');
zlabel('# of Photons (n/m^2)');

figure(4)
photons_per_area_transpose = permute(photons_per_area,[2 1 3]);
rotate3d on
colormap(flipud(hot))
[x,y,z] = meshgrid(speed_scatter, power_scatter, frequency_scatter);
scatter3(x(:),y(:),z(:),5,photons_per_area_transpose(:),'filled')
title('Photons per Square Meter')
xlabel('Speed (m/s)');
ylabel('Power (Watts)');
zlabel('Frequency (Hz)');
cb = colorbar;                                    
cb.Label.String = '# of Photons (n/m^2)';


u = unique(photons_per_area);
[n, edges] = histcounts(photons_per_area,u);
multiples = u(n > 3);

min_photons = sort(multiples, 'ascend');
min_photons = min_photons(1:15);

size(min_photons)

for mult=1:length(min_photons)
    inds = find(ismember(photons_per_area,min_photons(mult)));
    setting = zeros(size(inds,1),3);

    for ind=1:length(inds)
        [i,j,k] = ind2sub(size(photons_per_area), inds(ind));
        l = i * 0.1183; %speed
        m = j * 2000; %frequency
        n = k * 2.66; %power
        setting(ind,:) = [l,m,n];
    end
    
    settings{mult} = setting
end


